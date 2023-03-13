from typing import Optional, Sequence, Mapping

from constructs import Construct

from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_ecs as ecs
from aws_cdk import Duration
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_logs as logs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_autoscaling as autoscaling

from aws_fbm.fbm_file_system import FbmVolume, FbmFileSystem


class EC2Service(Construct):
    """Create an EC2 service for running a Docker container"""
    def __init__(
        self,
        scope: Construct,
        id: str,
        vpc: ec2.Vpc,
        cluster: ecs.Cluster,
        cpu: int,
        gpu_count: int,
        memory_limit_mib: int,
        docker_image_asset: ecr_assets.DockerImageAsset,
        task_name: str,
        file_system: FbmFileSystem,
        entry_point: Optional[Sequence[str]] = None,
        environment: Optional[Mapping[str, str]] = None,
        volumes: Optional[Sequence[FbmVolume]] = None
    ):
        super().__init__(scope, id)
        volumes = volumes or []

        # Create the task definition
        self.task_definition = ecs.Ec2TaskDefinition(
            self,
            id="Ec2TaskDefinition",
            task_role=self.create_task_role(),
            execution_role=self.create_execution_role(),
        )

        # GPU AMI
        machine_image = ecs.EcsOptimizedImage.amazon_linux2(
            hardware_type=ecs.AmiHardwareType.GPU)

        # Custom UserData so the EC2 instance registers with the correct cluster
        # when it launches
        user_data = ec2.UserData.for_linux()
        # Tell ECS to use GPU
        user_data.add_commands(f'echo "ECS_ENABLE_GPU_SUPPORT=true" >> /etc/ecs/ecs.config')
        # Register cluster - not required if using the default cluster
        user_data.add_commands(f'echo "ECS_CLUSTER={cluster.cluster_name}" >> /etc/ecs/ecs.config')

        template_security_group = ec2.SecurityGroup(
            self, "LaunchTemplateSG", vpc=vpc)

        # Allow service to access EFS file system
        template_security_group.connections.allow_to(
            other=file_system.file_system,
            port_range=ec2.Port.tcp(2049),
            description='Allow access to file system from Fargate service'
        )

        launch_template = ec2.LaunchTemplate(
            self,
            "ASG-LaunchTemplate",
            instance_type=ec2.InstanceType("g3s.xlarge"),
            machine_image=machine_image,
            user_data=user_data,
            role=self.create_launch_role(),
            security_group=template_security_group,
            detailed_monitoring=True
         )

        self.auto_scaling_group = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            launch_template=launch_template,
            min_capacity=0,
            cooldown=Duration.seconds(60)
        )

        self.capacity_provider = ecs.AsgCapacityProvider(
            self,
            "AsgCapacityProvider",
            auto_scaling_group=self.auto_scaling_group,
            machine_image_type=ecs.MachineImageType.AMAZON_LINUX_2,
            enable_managed_termination_protection=False
        )

        cluster.add_asg_capacity_provider(self.capacity_provider)

        # Add volumes
        for volume in volumes:
            self.task_definition.add_volume(
                name=volume.volume_name,
                efs_volume_configuration=ecs.EfsVolumeConfiguration(
                    file_system_id=volume.file_system_id,
                    # Note: when using an access point id, the root directory is
                    # relative to the access point
                    root_directory='/',
                    transit_encryption="ENABLED",
                    authorization_config=ecs.AuthorizationConfig(
                        access_point_id=volume.access_point.access_point_id,
                        iam="ENABLED"
                    )
                )
            )

        # Add the Docker container
        self.container = self.task_definition.add_container(
            id=task_name,
            image=ecs.ContainerImage.from_docker_image_asset(docker_image_asset),
            environment=environment,
            gpu_count=gpu_count,
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            entry_point=entry_point,
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix=task_name,
                log_retention=logs.RetentionDays.THREE_DAYS)
        )

        # Add mount points to the container
        for volume in volumes:
            self.container.add_mount_points(ecs.MountPoint(
                source_volume=volume.volume_name,
                container_path=volume.mount_dir,
                read_only=False
            ))

        # Create the service
        # Min and max healthy percents are chosen to ensure the single
        # provisioned EC2 can be updated by removing the existing task
        # before deploying the updated task.
        self.service = ecs.Ec2Service(
            self,
            "Ec2Service",
            cluster=cluster,
            desired_count=1,
            min_healthy_percent=0,
            max_healthy_percent=100,
            task_definition=self.task_definition,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True)
        )

    def create_task_role(self):
        """Create IAM role to be used by the ECS tasks.
        https://docs.aws.amazon.com/AmazonECS/latest/developerguide/instance_IAM_role.html
        """
        ecs_task_role = iam.Role(
            self,
            id="TaskRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )

        ecs_task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryReadOnly'))
        ecs_task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'))
        ecs_task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3ReadOnlyAccess'))
        ecs_task_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonElasticFileSystemFullAccess'))

        return ecs_task_role

    def create_execution_role(self):
        """Create IAM role to be used to create ECS tasks
        https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html
        """
        ecs_execution_role = iam.Role(
            self,
            "ExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        ecs_execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryReadOnly'))
        ecs_execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'))
        ecs_execution_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonElasticFileSystemReadOnlyAccess'))

        return ecs_execution_role

    def create_launch_role(self):
        """Create IAM role to be used to launch EC2 instances"""
        ec2_launch_role = iam.Role(
            self,
            id="Ec2ServiceRole",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com")
        )
        ec2_launch_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonEC2ContainerServiceforEC2Role'))
        ec2_launch_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMManagedInstanceCore'))
        return ec2_launch_role

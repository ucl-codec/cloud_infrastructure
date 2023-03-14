from typing import Optional, Sequence, Mapping
from aws_fbm.fbm_constructs.roles import EcsExecutionRole, EcsTaskRole, \
    Ec2LaunchRole

from constructs import Construct

from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_logs as logs
from aws_cdk import aws_iam as iam
from aws_cdk import aws_autoscaling as autoscaling

from aws_fbm.fbm_constructs.file_system import Volume, FileSystem


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
        file_system: FileSystem,
        entry_point: Optional[Sequence[str]] = None,
        environment: Optional[Mapping[str, str]] = None,
        volumes: Optional[Sequence[Volume]] = None
    ):
        super().__init__(scope, id)
        volumes = volumes or []

        # Create the task definition
        self.task_definition = ecs.Ec2TaskDefinition(
            self,
            id="Ec2TaskDefinition",
            task_role=EcsTaskRole(scope=self),
            execution_role=EcsExecutionRole(scope=self),
            volumes=[ecs.Volume(
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
                )) for volume in volumes]
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
        # user_data.add_commands(f'echo "ECS_CLUSTER={cluster.cluster_name}" >> /etc/ecs/ecs.config')

        template_security_group = ec2.SecurityGroup(
            self, "LaunchTemplateSG", vpc=vpc)

        # Allow service to access EFS file system
        # file_system.file_system.connections.allow_from(
        #     other=template_security_group,
        #     port_range=ec2.Port.tcp(2049),
        #     description='Allow access to file system from Fargate service'
        # )
        template_security_group.connections.allow_to(
            other=file_system.file_system,
            port_range=ec2.Port.tcp(2049),
            description='Allow access to file system from Fargate service'
        )
        # template_security_group.connections.allow_to(
        #     other=file_system.file_system,
        #     port_range=ec2.Port.tcp(2049),
        #     description='Allow access to file system from Fargate service'
        # )

        launch_template = ec2.LaunchTemplate(
            self,
            "ASG-LaunchTemplate",
            instance_type=ec2.InstanceType("g3s.xlarge"),
            machine_image=machine_image,
            user_data=user_data,
            security_group=template_security_group,
            role=Ec2LaunchRole(scope=self),
            detailed_monitoring=True
         )

        self.auto_scaling_group = autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            launch_template=launch_template,
            # desired_capacity=1,
            # # desired_capacity=0,
            min_capacity=0,
            desired_capacity=1,
            max_capacity=2,
            # min_capacity=0,
            # cooldown=Duration.seconds(60)
        )

        self.capacity_provider = ecs.AsgCapacityProvider(
            self,
            "AsgCapacityProvider",
            auto_scaling_group=self.auto_scaling_group,
            # machine_image_type=ecs.MachineImageType.AMAZON_LINUX_2,
            enable_managed_termination_protection=False
        )

        cluster.add_asg_capacity_provider(self.capacity_provider)


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
            # desired_count=1,
            # min_healthy_percent=50,
            # max_healthy_percent=200,
            # min_healthy_percent=0,
            # max_healthy_percent=100,
            task_definition=self.task_definition,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            capacity_provider_strategies=[ecs.CapacityProviderStrategy(
                capacity_provider=self.capacity_provider.capacity_provider_name,
                weight=1
            )]
        )


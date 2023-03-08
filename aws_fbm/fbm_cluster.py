from typing import Optional, Sequence, Mapping

from constructs import Construct
from aws_cdk import aws_logs, aws_ecs, aws_servicediscovery, aws_iam, aws_ec2
from aws_cdk import aws_autoscaling
from aws_fbm.fbm_file_system import FbmVolume, FbmFileSystem


class FbmBaseServiceDef(Construct):

    def __init__(self,
                 scope: Construct,
                 id: str,
                 cluster: aws_ecs.Cluster,
                 dns_name: str,
                 dns_namespace: aws_servicediscovery.PrivateDnsNamespace):

        super().__init__(scope=scope, id=id)
        self.cluster = cluster
        self.dns_name = dns_name
        self.dns_namespace = dns_namespace

    def add_volume(self, volume: FbmVolume):
        self.task_definition.add_volume(
            name=volume.volume_name,
            efs_volume_configuration=aws_ecs.EfsVolumeConfiguration(
                file_system_id=volume.file_system_id,
                # Note: when using an access point id, the root directory is
                # relative to the access point
                root_directory='/',
                transit_encryption="ENABLED",
                authorization_config=aws_ecs.AuthorizationConfig(
                    access_point_id=volume.access_point.access_point_id,
                    iam="ENABLED"
                )
            )
        )

    def add_docker_container(self,
                             docker_image,
                             name,
                             cpu: int,
                             memory_limit_mib: int,
                             gpu_count: int = 0,
                             entry_point: Optional[Sequence[str]] = None,
                             environment: Optional[Mapping[str, str]] = None):
        """Run a Docker image as an ECR container. The Docker image will be
         built locally as part of the cdk deploy and uploaded to the ECR"""
        container = self.task_definition.add_container(
            name,
            image=aws_ecs.ContainerImage.from_docker_image_asset(docker_image),
            environment=environment,
            gpu_count=gpu_count,
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            entry_point=entry_point,
            logging=aws_ecs.LogDrivers.aws_logs(
                stream_prefix=name,
                log_retention=aws_logs.RetentionDays.THREE_DAYS)
        )
        return container

    def create_task_role(self):
        """Create IAM role to be used by the ECS tasks.
        https://docs.aws.amazon.com/AmazonECS/latest/developerguide/instance_IAM_role.html
        """
        ecs_task_role = aws_iam.Role(
            self,
            id="TaskRole",
            assumed_by=aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )

        ecs_task_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryReadOnly'))
        ecs_task_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'))
        ecs_task_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonS3ReadOnlyAccess'))
        ecs_task_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonElasticFileSystemFullAccess'))

        return ecs_task_role

    def create_execution_role(self):
        """Create IAM role to be used to create ECS tasks
        https://docs.aws.amazon.com/AmazonECS/latest/developerguide/task_execution_IAM_role.html
        """
        ecs_execution_role = aws_iam.Role(
            self,
            "ExecutionRole",
            assumed_by=aws_iam.ServicePrincipal("ecs-tasks.amazonaws.com")
        )
        ecs_execution_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEC2ContainerRegistryReadOnly'))
        ecs_execution_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('CloudWatchLogsFullAccess'))
        ecs_execution_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('AmazonElasticFileSystemReadOnlyAccess'))

        return ecs_execution_role


class FbmFargateServiceDef(FbmBaseServiceDef):
    def __init__(self,
                 scope: Construct,
                 id: str,
                 cluster: aws_ecs.Cluster,
                 dns_namespace: aws_servicediscovery.PrivateDnsNamespace,
                 dns_name: str,
                 cpu: int,
                 memory_limit_mib: int,
                 ephemeral_storage_gib: int):
        super().__init__(scope, id=id, dns_name=dns_name, cluster=cluster,
                         dns_namespace=dns_namespace)
        self.task_definition = aws_ecs.FargateTaskDefinition(
            self,
            id="FargateTaskDefinition",
            task_role=self.create_task_role(),
            execution_role=self.create_execution_role(),
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            ephemeral_storage_gib=ephemeral_storage_gib
        )


class FbmEC2ServiceDef(FbmBaseServiceDef):
    def __init__(
            self,
            scope: Construct,
            id: str,
            cluster: aws_ecs.Cluster,
            dns_namespace: aws_servicediscovery.PrivateDnsNamespace,
            dns_name: str,
            file_system: FbmFileSystem,
            vpc: aws_ec2.Vpc):
        super().__init__(scope, id=id, dns_name=dns_name,
                         dns_namespace=dns_namespace,
                         cluster=cluster)

        """Create EC2 task definition"""
        self.task_definition = aws_ecs.Ec2TaskDefinition(
            self,
            "Ec2TaskDefinition",
            task_role=self.create_task_role(),
            execution_role=self.create_execution_role(),
        )

        # GPU AMI
        machine_image = aws_ecs.EcsOptimizedImage.amazon_linux2(
            hardware_type=aws_ecs.AmiHardwareType.GPU)

        # Custom UserData so the EC2 instance registers with the correct cluster
        # when it launches
        user_data = aws_ec2.UserData.for_linux()
        user_data.add_commands(f'echo "ECS_CLUSTER={cluster.cluster_name}" >> /etc/ecs/ecs.config')

        template_security_group = aws_ec2.SecurityGroup(
            self, "LaunchTemplateSG", vpc=vpc)
        file_system.allow_access_from_service(template_security_group)

        launch_role = aws_iam.Role(
            self,
            id="Ec2ServiceRole",
            assumed_by=aws_iam.ServicePrincipal("ec2.amazonaws.com")
        )
        launch_role.add_managed_policy(aws_iam.ManagedPolicy.from_aws_managed_policy_name('service-role/AmazonEC2ContainerServiceforEC2Role'))

        launch_template = aws_ec2.LaunchTemplate(
            self,
            "ASG-LaunchTemplate",
            instance_type=aws_ec2.InstanceType("g3s.xlarge"),
            machine_image=machine_image,
            user_data=user_data,
            role=launch_role,
            security_group=template_security_group
         )

        auto_scaling_group = aws_autoscaling.AutoScalingGroup(
            self,
            "ASG",
            vpc=vpc,
            launch_template=launch_template,
            desired_capacity=1,
            max_capacity=1
        )

        self.capacity_provider = aws_ecs.AsgCapacityProvider(
            self,
            "AsgCapacityProvider",
            auto_scaling_group=auto_scaling_group,
            machine_image_type=aws_ecs.MachineImageType.AMAZON_LINUX_2
        )

        self.cluster.add_asg_capacity_provider(self.capacity_provider)

    def create_service(self) -> aws_ecs.Ec2Service:

        return aws_ecs.Ec2Service(
            self,
            "Ec2Service",
            cluster=self.cluster,
            desired_count=1,
            min_healthy_percent=0,
            max_healthy_percent=100,
            task_definition=self.task_definition,
            circuit_breaker=aws_ecs.DeploymentCircuitBreaker(rollback=True)
        )

from typing import Optional, Sequence, Mapping

from constructs import Construct

from aws_cdk import aws_servicediscovery as servicediscovery
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_logs as logs
from aws_cdk import aws_iam as iam

from aws_fbm.fbm_file_system import FbmVolume


class FargateService(Construct):
    """Create a Fargate service for running a Docker container"""
    def __init__(
        self,
        scope: Construct,
        id: str,
        cluster: ecs.Cluster,
        dns_namespace: servicediscovery.PrivateDnsNamespace,
        dns_name: str,
        dns_domain: str,
        cpu: int,
        memory_limit_mib: int,
        ephemeral_storage_gib: int,
        docker_image_asset: ecr_assets.DockerImageAsset,
        task_name: str,
        port: int,
        permitted_client_ip_range: str,
        entry_point: Optional[Sequence[str]] = None,
        environment: Optional[Mapping[str, str]] = None,
        volumes: Optional[Sequence[FbmVolume]] = None
    ):
        super().__init__(scope, id)
        volumes = volumes or []

        # Create the task definition
        self.task_definition = ecs.FargateTaskDefinition(
            self,
            id="FargateTaskDefinition",
            task_role=self.create_task_role(),
            execution_role=self.create_execution_role(),
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            ephemeral_storage_gib=ephemeral_storage_gib
        )

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
            gpu_count=0,
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            entry_point=entry_point,
            port_mappings=[ecs.PortMapping(container_port=port)],
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
        self.service = ecs.FargateService(
            self,
            "FargateService",
            cluster=cluster,
            desired_count=1,
            task_definition=self.task_definition,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            cloud_map_options=ecs.CloudMapOptions(
                name=dns_name,
                cloud_map_namespace=dns_namespace,
                dns_record_type=servicediscovery.DnsRecordType.A
            )
        )

        # Open the service to incoming connections
        self.service.connections.allow_from(
            ec2.Peer.ipv4(permitted_client_ip_range), ec2.Port.tcp(port))

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

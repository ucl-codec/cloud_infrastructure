from aws_fbm.fbm_constructs.file_system import Volume, FileSystem

from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs_patterns as ecs_patterns
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_route53 as route53
from aws_cdk import aws_logs as logs
from aws_cdk import aws_iam as iam

from typing import Optional, Sequence, Mapping

from constructs import Construct


class FargateService(Construct):
    """Create a Fargate service for running a Docker container"""
    
    def __init__(
        self,
        scope: Construct,
        id: str,
        cluster: ecs.Cluster,
        dns_name: str,
        domain_zone: route53.IHostedZone,
        cpu: int,
        memory_limit_mib: int,
        ephemeral_storage_gib: int,
        docker_image_asset: ecr_assets.DockerImageAsset,
        task_name: str,
        container_port: int,
        listener_port: int,
        permitted_client_ip_range: str,
        file_system: Optional[FileSystem] = None,
        entry_point: Optional[Sequence[str]] = None,
        environment: Optional[Mapping[str, str]] = None,
        volumes: Optional[Sequence[Volume]] = None
    ):
        super().__init__(scope, id)
        self.listener_port = listener_port

        if volumes and not file_system:
            raise RuntimeError("file_system must be specified if volumes are"
                               "specified")
        volumes = volumes or []

        # Create the task definition
        self.task_definition = ecs.FargateTaskDefinition(
            self,
            id="FargateTaskDefinition",
            task_role=EcsTaskRole(scope=self),
            execution_role=EcsExecutionRole(scope=self),
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            ephemeral_storage_gib=ephemeral_storage_gib,
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

        # Add the Docker container
        self.container = self.task_definition.add_container(
            id=task_name,
            image=ecs.ContainerImage.from_docker_image_asset(docker_image_asset),
            environment=environment,
            gpu_count=0,
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            entry_point=entry_point,
            port_mappings=[ecs.PortMapping(container_port=container_port)],
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
        self.load_balanced_service = self.create_service(
            cluster=cluster,
            listener_port=listener_port,
            container_port=container_port,
            container_name=task_name,
            dns_name=dns_name,
            domain_zone=domain_zone
        )

        self.service = self.load_balanced_service.service
        self.load_balancer = self.load_balanced_service.load_balancer

        # Allow service to access EFS file system
        if file_system:
            self.service.connections.allow_to(
                other=file_system.file_system,
                port_range=ec2.Port.tcp(2049),
                description='Allow access to file system from Fargate service'
            )

        # Open the service to incoming connections
        self.allow_from(permitted_client_ip_range)


    def create_service(self,
                       cluster: ecs.Cluster,
                       listener_port: int,
                       container_port: int,
                       container_name: str,
                       dns_name: str,
                       domain_zone: route53.IHostedZone):
        """Create the load balanced service"""
        raise NotImplementedError

    def allow_from(self, cidr_range: str):
        """Permit access to this service from the given range"""
        raise NotImplementedError


class HttpService(FargateService):
    """A Fargate service corresponding to an http server"""

    def create_service(self,
                       cluster: ecs.Cluster,
                       listener_port: int,
                       container_port: int,
                       container_name: str,
                       dns_name: str,
                       domain_zone: route53.IHostedZone):
        return ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "LbFargateService",
            cluster=cluster,
            desired_count=1,
            task_definition=self.task_definition,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            assign_public_ip=False,
            domain_name=dns_name,
            listener_port=listener_port,
            open_listener=False,
            public_load_balancer=False,
            domain_zone=domain_zone
        )

    def allow_from(self, cidr_range: str):
        self.load_balancer.connections.allow_from(
            ec2.Peer.ipv4(cidr_range),
            ec2.Port.tcp(self.listener_port))


class TcpService(FargateService):
    """A Fargate service corresponding to a tcp server"""

    def create_service(self,
                       cluster: ecs.Cluster,
                       listener_port: int,
                       container_port: int,
                       container_name: str,
                       dns_name: str,
                       domain_zone: route53.IHostedZone):
        load_balanced_service = ecs_patterns.NetworkLoadBalancedFargateService(
            self, "LbFargateService",
            cluster=cluster,
            desired_count=1,
            task_definition=self.task_definition,
            circuit_breaker=ecs.DeploymentCircuitBreaker(rollback=True),
            assign_public_ip=False,
            domain_name=dns_name,
            listener_port=listener_port,
            public_load_balancer=False,
            domain_zone=domain_zone
        )
        return load_balanced_service

    def allow_from(self, cidr_range: str):
        self.service.connections.allow_from(
            ec2.Peer.ipv4(cidr_range),
            ec2.Port.tcp(self.listener_port))

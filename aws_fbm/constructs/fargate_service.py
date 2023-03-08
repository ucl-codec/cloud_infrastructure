from typing import Optional, Sequence, Mapping

from constructs import Construct

from aws_fbm.fbm_cluster import FbmFargateServiceDef
from aws_cdk import aws_servicediscovery as servicediscovery
from aws_cdk import aws_ecr_assets as ecr_assets
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ec2 as ec2

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

        self.service_def = FbmFargateServiceDef(
            scope=self,
            id="ServiceDefinition",
            cluster=cluster,
            dns_namespace=dns_namespace,
            dns_name=dns_name,
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            ephemeral_storage_gib=ephemeral_storage_gib
        )
        for volume in volumes:
            self.service_def.add_volume(volume=volume)
        self.container = self.service_def.add_docker_container(
            docker_image=docker_image_asset,
            name=task_name,
            cpu=cpu,
            memory_limit_mib=memory_limit_mib,
            entry_point=entry_point,
            environment=environment
        )

        # Expose ports from the container
        self.container.add_port_mappings(
            ecs.PortMapping(container_port=port))

        # Add mount points to the container
        for volume in volumes:
            self.container.add_mount_points(ecs.MountPoint(
                source_volume=volume.volume_name,
                container_path=volume.mount_dir,
                read_only=False
            ))

        # Create the service
        self.service = self.service_def.create_service()

        # Open the service to incoming connections
        self.service.connections.allow_from(
            ec2.Peer.ipv4(permitted_client_ip_range), ec2.Port.tcp(port))

from constructs import Construct

from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.fbm_cluster import FbmFargateServiceDef
from aws_fbm.utils import repo_path
from aws_cdk import (aws_ecs as ecs)
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk import aws_ec2 as ec2


class FbmNetworkStack(FbmBaseStack):

    def __init__(self, scope: Construct, construct_id: str,
                 stack_name: str,
                 dns_domain: str,
                 description: str,
                 network_number: int,
                 **kwargs) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         description=description,
                         network_number=network_number,
                         **kwargs)

        self.dns_domain = dns_domain
        self.add_vpn()
        self.network_dns_host = "network"
        self.jupyter_dns_host = "jupyter"
        self.tensorboard_dns_host = "tensorboard"
        self.add_dns(namespace=self.dns_domain)

        self.mqtt_broker = f"{self.network_dns_host}.{self.dns_domain}"
        self.mqtt_broker_port = "1883"
        self.uploads_port = "8000"
        self.uploads_url = f"http://{self.network_dns_host}.{self.dns_domain}:{self.uploads_port}/upload/"

        # Create task definition
        self.network_service_def = FbmFargateServiceDef(
            scope=self,
            id="NetworkServiceDef",
            cluster=self.cluster,
            dns_namespace=self.dns_namespace,
            dns_name=self.network_dns_host,
            cpu=1024,
            memory_limit_mib=8192,
            ephemeral_storage_gib=40
        )
        # MQTT container
        mqtt_docker_image = DockerImageAsset(
            self,
            id="mqtt",
            directory=str(repo_path() / "docker" / "mqtt"),
            file='Dockerfile'
        )
        mqtt_container = self.network_service_def.add_docker_container(
            mqtt_docker_image,
            name="mqtt",
            cpu=512,
            memory_limit_mib=4096
        )
        mqtt_container.add_port_mappings(
            ecs.PortMapping(container_port=1883))

        # Restful container
        restful_docker_image = DockerImageAsset(
            self,
            id="restful",
            directory=str(repo_path() / "docker" / "restful"),
            file='Dockerfile'
        )
        restful_container = self.network_service_def.add_docker_container(
            restful_docker_image,
            name="restful",
            cpu=512,
            memory_limit_mib=4096
        )
        restful_container.add_port_mappings(
            ecs.PortMapping(container_port=8000))
        self.network_service = self.network_service_def.create_service()

        # Allow connections from researcher services
        self.network_service.connections.allow_from(
            ec2.Peer.ipv4(self.cidr_range), ec2.Port.tcp(1883))
        self.network_service.connections.allow_from(
            ec2.Peer.ipv4(self.cidr_range), ec2.Port.tcp(8000))

        # Jupyter service
        self.researcher_service_def = FbmFargateServiceDef(
            scope=self,
            id="JupyterServiceDef",
            cluster=self.cluster,
            dns_namespace=self.dns_namespace,
            dns_name=self.jupyter_dns_host,
            cpu=2048,
            memory_limit_mib=16384,
            ephemeral_storage_gib=40
        )
        # Researcher container
        researcher_docker_image = DockerImageAsset(
            self,
            id="researcher",
            directory=str(repo_path() / "docker"),
            file="researcher/Dockerfile"
        )
        researcher_container = self.researcher_service_def.add_docker_container(
            researcher_docker_image,
            name="researcher",
            environment={
                "MQTT_BROKER": self.mqtt_broker,
                "MQTT_BROKER_PORT": self.mqtt_broker_port,
                "UPLOADS_URL": self.uploads_url},
            cpu=2048,
            memory_limit_mib=16384,
            entry_point=["/entrypoint_jupyter.bash"]
        )
        # Jupyter
        researcher_container.add_port_mappings(
            ecs.PortMapping(container_port=8888))
        self.researcher_service = self.researcher_service_def.create_service()
        for port in [8888]:
            self.researcher_service.connections.security_groups[0].add_ingress_rule(
                peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
                connection=ec2.Port.tcp(port),
                description=f"Allow http inbound from VPC on port {port}"
            )

        # Tensorboard service
        self.tensorboard_service_def = FbmFargateServiceDef(
            scope=self,
            id="ResearcherServiceDef",
            cluster=self.cluster,
            dns_namespace=self.dns_namespace,
            dns_name=self.tensorboard_dns_host,
            cpu=2048,
            memory_limit_mib=16384,
            ephemeral_storage_gib=40
        )
        tensorboard_container = self.tensorboard_service_def.add_docker_container(
            researcher_docker_image,
            name="tensorboard",
            environment={
                "MQTT_BROKER": self.mqtt_broker,
                "MQTT_BROKER_PORT": self.mqtt_broker_port,
                "UPLOADS_URL": self.uploads_url},
            cpu=2048,
            memory_limit_mib=16384,
            entry_point=["/entrypoint_tensorboard.bash"]
        )
        # Tensorboard
        tensorboard_container.add_port_mappings(
            ecs.PortMapping(container_port=6007))
        self.tensorboard_service = self.tensorboard_service_def.create_service()
        for port in [6007]:
            self.tensorboard_service.connections.security_groups[0].add_ingress_rule(
                peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
                connection=ec2.Port.tcp(port),
                description=f"Allow http inbound from VPC on port {port}"
            )

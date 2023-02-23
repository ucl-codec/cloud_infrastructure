from constructs import Construct

from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.utils import repo_path
from aws_cdk import (aws_ecs as ecs)


class FbmNetworkStack(FbmBaseStack):

    def __init__(self, scope: Construct, construct_id: str,
                 stack_name: str,
                 stack_prefix: str,
                 description: str,
                 network_number: int,
                 **kwargs) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         stack_prefix=stack_prefix,
                         description=description,
                         network_number=network_number,
                         cpu=2048,
                         memory_limit_mib=16384,
                         **kwargs)

        self.add_vpn()
        self.add_dns(namespace="passian.federated")

        mqtt_broker = "localhost"
        mqtt_broker_port = "1883"
        uploads_url = "http://localhost/upload/"

        # MQTT container
        mqtt_container = self.add_docker_container(
            name="mqtt",
            context_dir=str(repo_path() / "docker" / "mqtt"),
            path_to_dockerfile='Dockerfile'
        )
        mqtt_container.add_port_mappings(
            ecs.PortMapping(container_port=1883))

        # Restful container
        restful_container = self.add_docker_container(
            name="restful",
            context_dir=str(repo_path() / "docker" / "restful"),
            path_to_dockerfile='Dockerfile'
        )
        restful_container.add_port_mappings(
            ecs.PortMapping(container_port=8000))

        # Researcher container
        researcher_container = self.add_docker_container(
            name="researcher",
            context_dir=str(repo_path() / "docker"),
            path_to_dockerfile="researcher/Dockerfile",
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": mqtt_broker_port,
                "UPLOADS_URL": uploads_url}
        )
        # Jupyter and Tensorboard
        researcher_container.add_port_mappings(
            ecs.PortMapping(container_port=8888))
        researcher_container.add_port_mappings(
            ecs.PortMapping(container_port=6007))

        self.add_service(dns_name="researcher", ports=[8888, 6007])

from constructs import Construct

from aws_fbm.constructs.fargate_service import FargateService
from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.utils import repo_path
from aws_cdk.aws_ecr_assets import DockerImageAsset


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
        self.jupyter_port = 8888
        self.tensorboard_port = 6007
        self.restful_port = 8000
        self.mqtt_port = 1883
        self.restful_dns_host = "restful"
        self.mqtt_dns_host = "mqtt"
        self.jupyter_dns_host = "jupyter"
        self.tensorboard_dns_host = "tensorboard"
        self.add_dns(namespace=self.dns_domain)

        self.mqtt_broker = f"{self.mqtt_dns_host}.{self.dns_domain}"
        self.uploads_url = f"http://{self.restful_dns_host}.{self.dns_domain}:{self.restful_port}/upload/"

        # MQTT container
        mqtt_docker_image = DockerImageAsset(
            self,
            id="mqtt",
            directory=str(repo_path() / "docker" / "mqtt"),
            file='Dockerfile'
        )
        # Create mqtt service
        self.mqtt_service = FargateService(
            scope=self,
            id="MqttService",
            cluster=self.cluster,
            dns_namespace=self.dns_namespace,
            dns_name=self.mqtt_dns_host,
            dns_domain=self.dns_domain,
            cpu=512,
            memory_limit_mib=4096,
            ephemeral_storage_gib=40,
            docker_image_asset=mqtt_docker_image,
            task_name="mqtt",
            container_port=self.mqtt_port,
            listener_port=self.mqtt_port,
            permitted_client_ip_range=self.cidr_range
        )

        # Restful container
        restful_docker_image = DockerImageAsset(
            self,
            id="restful",
            directory=str(repo_path() / "docker" / "restful"),
            file='Dockerfile'
        )
        # Create restful service
        self.restful_service = FargateService(
            scope=self,
            id="RestfulService",
            cluster=self.cluster,
            dns_namespace=self.dns_namespace,
            dns_name=self.restful_dns_host,
            dns_domain=self.dns_domain,
            cpu=512,
            memory_limit_mib=4096,
            ephemeral_storage_gib=40,
            docker_image_asset=restful_docker_image,
            task_name="restful",
            container_port=self.restful_port,
            listener_port=self.restful_port,
            permitted_client_ip_range=self.cidr_range
        )

        # Common researcher container
        researcher_docker_image = DockerImageAsset(
            self,
            id="researcher",
            directory=str(repo_path() / "docker"),
            file="researcher/Dockerfile"
        )
        # Jupyter service using the common researcher container
        self.jupyter_service = FargateService(
            scope=self,
            id="JupyterService",
            cluster=self.cluster,
            dns_namespace=self.dns_namespace,
            dns_name=self.jupyter_dns_host,
            dns_domain=self.dns_domain,
            cpu=2048,
            memory_limit_mib=16384,
            ephemeral_storage_gib=40,
            docker_image_asset=researcher_docker_image,
            task_name="restful",
            container_port=self.jupyter_port,
            listener_port=self.jupyter_port,
            permitted_client_ip_range=self.cidr_range,
            entry_point=["/entrypoint_jupyter.bash"],
            environment={
                "MQTT_BROKER": self.mqtt_broker,
                "MQTT_BROKER_PORT": f"{self.mqtt_port}",
                "UPLOADS_URL": self.uploads_url},
        )

        # Tensorboard service using the common researcher container
        self.tensorboard_service = FargateService(
            scope=self,
            id="TensorboardService",
            cluster=self.cluster,
            dns_namespace=self.dns_namespace,
            dns_name=self.tensorboard_dns_host,
            dns_domain=self.dns_domain,
            cpu=2048,
            memory_limit_mib=16384,
            ephemeral_storage_gib=40,
            docker_image_asset=researcher_docker_image,
            task_name="restful",
            container_port=self.tensorboard_port,
            listener_port=self.tensorboard_port,
            permitted_client_ip_range=self.cidr_range,
            entry_point=["/entrypoint_tensorboard.bash"],
            environment={
                "MQTT_BROKER": self.mqtt_broker,
                "MQTT_BROKER_PORT": f"{self.mqtt_port}",
                "UPLOADS_URL": self.uploads_url},
        )

from aws_cdk import CfnOutput

from constructs import Construct

from aws_fbm.constructs.fargate_service import HttpService, TcpService
from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.utils import repo_path
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk import aws_ec2 as ec2
from aws_fbm.fbm_file_system import FbmFileSystem


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

        # Create file system and volumes
        self.file_system = FbmFileSystem(
            scope=self,
            id="FileSystem",
            vpc=self.vpc
        )
        researcher_config_volume = self.file_system.create_volume(
            name="config", root_directory='/researcher/config', mount_dir="/config")
        researcher_data_volume = self.file_system.create_volume(
            name="data", root_directory='/researcher/data', mount_dir="/data")
        researcher_etc_volume = self.file_system.create_volume(
            name="etc", root_directory='/researcher/etc', mount_dir="/fedbiomed/etc")
        researcher_runs_volume = self.file_system.create_volume(
            name="runs", root_directory='/researcher/runs', mount_dir="/fedbiomed/runs")
        researcher_var_volume = self.file_system.create_volume(
            name="var", root_directory='/researcher/var', mount_dir="/fedbiomed/var")
        researcher_notebooks_volume = self.file_system.create_volume(
            name="notebooks", root_directory='/researcher/notebooks', mount_dir="/fedbiomed/notebooks")

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

        CfnOutput(self, "MqttBroker",
                  export_name="FbmMqttBroker",
                  value=self.mqtt_broker,
                  description="Hostname of FBM MQTT broker")
        CfnOutput(self, "UploadsUrl",
                  export_name="FbmUploadsUrl",
                  value=self.uploads_url,
                  description="Hostname of FBM restful service")

        # MQTT container
        mqtt_docker_image = DockerImageAsset(
            self,
            id="mqtt",
            directory=str(repo_path() / "docker" / "mqtt"),
            file='Dockerfile'
        )
        # Create mqtt service
        self.mqtt_service = TcpService(
            scope=self,
            id="MqttService",
            cluster=self.cluster,
            dns_name=self.mqtt_dns_host,
            domain_zone=self.hosted_zone,
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
        self.restful_service = HttpService(
            scope=self,
            id="RestfulService",
            cluster=self.cluster,
            dns_name=self.restful_dns_host,
            domain_zone=self.hosted_zone,
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
        self.jupyter_service = HttpService(
            scope=self,
            id="JupyterService",
            cluster=self.cluster,
            dns_name=self.jupyter_dns_host,
            domain_zone=self.hosted_zone,
            cpu=2048,
            memory_limit_mib=16384,
            ephemeral_storage_gib=40,
            docker_image_asset=researcher_docker_image,
            task_name="jupyter",
            container_port=self.jupyter_port,
            listener_port=80,
            permitted_client_ip_range=self.cidr_range,
            file_system=self.file_system,
            entry_point=["/entrypoint_jupyter.bash"],
            environment={
                "MQTT_BROKER": self.mqtt_broker,
                "MQTT_BROKER_PORT": f"{self.mqtt_port}",
                "UPLOADS_URL": self.uploads_url},
            volumes=[researcher_config_volume, researcher_data_volume,
                     researcher_etc_volume, researcher_runs_volume,
                     researcher_var_volume, researcher_notebooks_volume]
        )
        self.jupyter_service.load_balanced_service.target_group.configure_health_check(
            path="/tree",
            healthy_http_codes="200,302,304"
        )

        # Tensorboard service using the common researcher container
        self.tensorboard_service = HttpService(
            scope=self,
            id="TensorboardService",
            cluster=self.cluster,
            dns_name=self.tensorboard_dns_host,
            domain_zone=self.hosted_zone,
            cpu=2048,
            memory_limit_mib=16384,
            ephemeral_storage_gib=40,
            docker_image_asset=researcher_docker_image,
            task_name="tensorboard",
            container_port=self.tensorboard_port,
            listener_port=80,
            permitted_client_ip_range=self.cidr_range,
            file_system=self.file_system,
            entry_point=["/entrypoint_tensorboard.bash"],
            environment={
                "MQTT_BROKER": self.mqtt_broker,
                "MQTT_BROKER_PORT": f"{self.mqtt_port}",
                "UPLOADS_URL": self.uploads_url},
            volumes=[researcher_config_volume, researcher_data_volume,
                     researcher_etc_volume, researcher_runs_volume,
                     researcher_var_volume, researcher_notebooks_volume]
        )

    def open_peer_ports(self, cidr_range: str):
        self.mqtt_service.service.connections.allow_from(
            ec2.Peer.ipv4(cidr_range), ec2.Port.tcp(1883))
        self.restful_service.load_balancer.connections.allow_from(
            ec2.Peer.ipv4(cidr_range), ec2.Port.tcp(8000))

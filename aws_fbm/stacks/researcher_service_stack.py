from aws_fbm.fbm_constructs.fargate_service import HttpService
from aws_fbm.stacks.network_stack import NetworkStack
from aws_fbm.utils.utils import repo_path
from aws_fbm.stacks.network_service_stack import NetworkServiceStack

from constructs import Construct
from aws_cdk import Stack
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk import aws_ecs as ecs
from aws_cdk import Environment


class ResearcherServiceStack(Stack):
    """CDK stack defining a cluster containing Fed-BioMed researcher services"""

    def __init__(self, scope: Construct, id: str,
                 network_stack: NetworkStack,
                 network_service_stack: NetworkServiceStack,
                 env: Environment):
        super().__init__(scope=scope, id=id,
                         description=f"FBM researcher services stack for "
                                     f"{network_stack.site_name}",
                         env=env)

        # Ports and hostnames
        self.jupyter_port = 8888
        self.tensorboard_port = 6007
        self.jupyter_dns_host = "jupyter"
        self.tensorboard_dns_host = "tensorboard"
        mqtt_broker = network_service_stack.mqtt_broker
        mqtt_port = network_service_stack.mqtt_port
        uploads_url = network_service_stack.uploads_url

        # Create cluster
        self.cluster = ecs.Cluster(scope=self, id="ResearcherCluster",
                                   container_insights=True,
                                   vpc=network_stack.vpc)

        file_system = network_stack.file_system

        # Volumes that can be shared between researcher services
        researcher_config_volume = file_system.create_volume(
            name="config",
            root_directory='/researcher/config',
            mount_dir="/config")
        researcher_data_volume = file_system.create_volume(
            name="data",
            root_directory='/researcher/data',
            mount_dir="/data")
        researcher_etc_volume = file_system.create_volume(
            name="etc",
            root_directory='/researcher/etc',
            mount_dir="/fedbiomed/etc")
        researcher_runs_volume = file_system.create_volume(
            name="runs",
            root_directory='/researcher/runs',
            mount_dir="/fedbiomed/runs")
        researcher_var_volume = file_system.create_volume(
            name="var",
            root_directory='/researcher/var',
            mount_dir="/fedbiomed/var")
        researcher_notebooks_volume = file_system.create_volume(
            name="notebooks",
            root_directory='/researcher/notebooks',
            mount_dir="/fedbiomed/notebooks")

        # Common researcher container - used by both jupyter and tensorboard
        # service, with different entrypoints
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
            domain_zone=network_stack.hosted_zone,
            cpu=2048,
            memory_limit_mib=16384,
            ephemeral_storage_gib=40,
            docker_image_asset=researcher_docker_image,
            task_name="jupyter",
            container_port=self.jupyter_port,
            listener_port=80,
            file_system=file_system,
            entry_point=["/entrypoint_jupyter.bash"],
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": f"{mqtt_port}",
                "UPLOADS_URL": uploads_url},
            volumes=[researcher_config_volume, researcher_data_volume,
                     researcher_etc_volume, researcher_runs_volume,
                     researcher_var_volume, researcher_notebooks_volume]
        )
        # Configure expected healthy return codes from the web interface
        self.jupyter_service.load_balanced_service.target_group.\
            configure_health_check(path="/tree",
                                   healthy_http_codes="200,302,304")
        # Allow connections from network VPN
        self.jupyter_service.allow_from_ip_range(network_stack.cidr_range)

        # Tensorboard service using the common researcher container
        self.tensorboard_service = HttpService(
            scope=self,
            id="TensorboardService",
            cluster=self.cluster,
            dns_name=self.tensorboard_dns_host,
            domain_zone=network_stack.hosted_zone,
            cpu=2048,
            memory_limit_mib=16384,
            ephemeral_storage_gib=40,
            docker_image_asset=researcher_docker_image,
            task_name="tensorboard",
            container_port=self.tensorboard_port,
            listener_port=80,
            file_system=file_system,
            entry_point=["/entrypoint_tensorboard.bash"],
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": f"{mqtt_port}",
                "UPLOADS_URL": uploads_url},
            volumes=[researcher_config_volume, researcher_data_volume,
                     researcher_etc_volume, researcher_runs_volume,
                     researcher_var_volume, researcher_notebooks_volume]
        )
        # Allow connections from network VPN
        self.tensorboard_service.allow_from_ip_range(network_stack.cidr_range)

        # Allow researcher components to connect to the network stack
        network_service_stack.allow_from_ip_range(network_stack.cidr_range)

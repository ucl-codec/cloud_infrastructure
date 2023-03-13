from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.fbm_file_system import FbmFileSystem
from aws_fbm.utils import repo_path
from aws_fbm.constructs.ec2_service import EC2Service
from aws_fbm.constructs.fargate_service import HttpService
from aws_fbm.fbm_node_stack import FbmNodeStack

from aws_cdk import Environment, Stack
from aws_cdk import aws_ecs as ecs
from aws_cdk.aws_ecr_assets import DockerImageAsset
from constructs import Construct


class NodeServiceStack(Stack):
    def __init__(self, scope: Construct, id: str,
                 network_stack: FbmNetworkStack,
                 node_stack: FbmNodeStack,
                 env: Environment):
        super().__init__(
            scope=scope,
            id=id,
            description=f"FBM network services stack for {node_stack.site_name}",
            env=env)

        self.gui_dns_host = "gui"

        # Create cluster
        self.cluster = ecs.Cluster(
            scope=self, id="Cluster", container_insights=True,
            vpc=node_stack.vpc)

        file_system = node_stack.file_system

        node_config_volume = file_system.create_volume(
            name="config", root_directory='/node/config', mount_dir="/config")
        node_data_volume = file_system.create_volume(
            name="data", root_directory='/node/data', mount_dir="/data")
        node_etc_volume = file_system.create_volume(
            name="etc", root_directory='/node/etc', mount_dir="/fedbiomed/etc")
        node_var_volume = file_system.create_volume(
            name="var", root_directory='/node/var', mount_dir="/fedbiomed/var")
        node_common_volume = file_system.create_volume(
            name="common", root_directory='/node/common',
            mount_dir="/fedbiomed/envs/common")

        mqtt_broker = network_stack.mqtt_broker
        mqtt_port = network_stack.mqtt_port
        uploads_url = network_stack.uploads_url

        # Docker image for node
        node_docker_image = DockerImageAsset(
            self,
            id="node",
            directory=str(repo_path() / "docker"),
            file="node/Dockerfile"
        )
        # Create node service
        self.node_service = EC2Service(
            scope=self,
            id="NodeService",
            vpc=node_stack.vpc,
            cluster=self.cluster,
            cpu=4096,
            gpu_count=1,
            memory_limit_mib=30000,
            docker_image_asset=node_docker_image,
            task_name="node",
            file_system=file_system,
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": f"{mqtt_port}",
                "UPLOADS_URL": uploads_url},
            volumes=[node_config_volume, node_data_volume, node_etc_volume,
                     node_var_volume, node_common_volume]
        )

        # Docker image for gui
        gui_docker_image = DockerImageAsset(
            self,
            id="gui",
            directory=str(repo_path() / "docker"),
            file="gui/Dockerfile"
        )
        # Create gui service
        self.gui_service = HttpService(
            scope=self,
            id="GuiService",
            cluster=self.cluster,
            dns_name=self.gui_dns_host,
            domain_zone=node_stack.hosted_zone,
            cpu=4096,
            memory_limit_mib=30720,
            ephemeral_storage_gib=100,
            docker_image_asset=gui_docker_image,
            task_name="gui",
            container_port=8484,
            listener_port=80,
            permitted_client_ip_range=node_stack.cidr_range,
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": f"{mqtt_port}",
                "UPLOADS_URL": uploads_url},
            file_system=file_system,
            volumes=[node_data_volume, node_etc_volume, node_var_volume,
                     node_common_volume]
        )
        self.gui_service.load_balanced_service.target_group.\
            configure_health_check(healthy_http_codes="200,304")

        # Do this here after the stack has been created
        network_stack.open_peer_ports(node_stack.cidr_range)

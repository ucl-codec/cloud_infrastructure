from aws_fbm.fbm_constructs.fargate_service import HttpService, TcpService
from aws_fbm.stacks.network_stack import NetworkStack
from aws_fbm.utils.utils import repo_path

from constructs import Construct
from aws_cdk import Stack
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk import aws_ecs as ecs
from aws_cdk import Environment


class NetworkServiceStack(Stack):
    """CDK stack defining a cluster containing Fed-BioMed network services

    This stack does not generally contain stateful resources (such as the
    VPN or file system); therefore this stack can be destroyed and re-created
    without affecting the rest of the system

    Stateful resources are defined in the NetworkStack
    """

    def __init__(self, scope: Construct,
                 network_stack: NetworkStack,
                 env: Environment):
        super().__init__(scope=scope,
                         id=f"{network_stack.name_prefix}NetworkServiceStack",
                         description=f"FBM network services stack for "
                                     f"{network_stack.site_description}",
                         env=env)

        # Ports and hostnames
        self.restful_port = 8000
        self.mqtt_port = 1883
        self.restful_dns_host = f"restful.{network_stack.dns_domain}"
        self.mqtt_dns_host = f"mqtt.{network_stack.dns_domain}"
        protocol = 'https://' if network_stack.use_https else 'http://'

        self.mqtt_broker = f"{self.mqtt_dns_host}"
        self.uploads_url = f"{protocol}{self.restful_dns_host}" \
                           f":{self.restful_port}/upload/"

        # Create cluster
        self.cluster = ecs.Cluster(scope=self, id="NetworkCluster",
                                   container_insights=True,
                                   vpc=network_stack.vpc)

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
            domain_zone=network_stack.hosted_zone,
            cpu=512,
            memory_limit_mib=4096,
            ephemeral_storage_gib=40,
            docker_image_asset=mqtt_docker_image,
            task_name="mqtt",
            container_port=self.mqtt_port,
            listener_port=self.mqtt_port,
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
            domain_zone=network_stack.hosted_zone,
            cpu=512,
            memory_limit_mib=4096,
            ephemeral_storage_gib=40,
            docker_image_asset=restful_docker_image,
            task_name="restful",
            container_port=self.restful_port,
            listener_port=self.restful_port,
        )

    def allow_from_ip_range(self, cidr_range: str):
        """Allow connections to network services from the given cidr range"""
        self.mqtt_service.allow_from_ip_range(cidr_range)
        self.restful_service.allow_from_ip_range(cidr_range)

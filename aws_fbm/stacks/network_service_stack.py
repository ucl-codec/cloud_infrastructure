from aws_fbm.constructs.fargate_service import HttpService, TcpService
from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.utils import repo_path

from constructs import Construct
from aws_cdk import CfnOutput, Stack
from aws_cdk.aws_ecr_assets import DockerImageAsset
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import Environment


class NetworkServiceStack(Stack):
    """CDK stack defining a cluster containing Fed-BioMed network services"""

    def __init__(self, scope: Construct, id: str,
                 network_stack: FbmNetworkStack,
                 env: Environment):
        super().__init__(
            scope=scope,
            id=id,
            description=f"FBM network services stack for "
                        f"{network_stack.site_name}",
            env=env)

        # Ports and hostnames
        self.restful_port = 8000
        self.mqtt_port = 1883
        self.restful_dns_host = "restful"
        self.mqtt_dns_host = "mqtt"

        self.mqtt_broker = f"{self.mqtt_dns_host}.{network_stack.dns_domain}"
        self.uploads_url = f"http://{self.restful_dns_host}." \
                           f"{network_stack.dns_domain}:{self.restful_port}/upload/"

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
            permitted_client_ip_range=network_stack.cidr_range
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
            permitted_client_ip_range=network_stack.cidr_range
        )

        CfnOutput(self, "MqttBroker",
                  export_name="FbmMqttBroker",
                  value=self.mqtt_broker,
                  description="Hostname of FBM MQTT broker")
        CfnOutput(self, "UploadsUrl",
                  export_name="FbmUploadsUrl",
                  value=self.uploads_url,
                  description="Hostname of FBM restful service")

    def allow_from(self, cidr_range: str):
        """Allow connections to network services from the given cidr range"""
        self.mqtt_service.allow_from(cidr_range)
        self.restful_service.allow_from(cidr_range)

from aws_fbm.constructs.fargate_service import FargateService
from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.fbm_data_sync import FbmDataSync
from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.fbm_file_system import FbmFileSystem
from aws_fbm.utils import repo_path
from aws_cdk import custom_resources, Environment
from aws_cdk import aws_ec2 as ec2, aws_iam

from constructs import Construct
import aws_cdk.aws_logs as logs
from aws_cdk.aws_ecr_assets import DockerImageAsset

from aws_fbm.constructs.ec2_service import EC2Service


class FbmNodeStack(FbmBaseStack):

    def __init__(self, scope: Construct, construct_id: str,
                 site_name: str,
                 stack_name: str,
                 dns_domain: str,
                 bucket_name: str,
                 description: str,
                 network_number: int,
                 network_stack: FbmNetworkStack,
                 network_vpc: ec2.Vpc,
                 env: Environment) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         description=description,
                         network_number=network_number,
                         env=env)
        self.dns_domain = dns_domain
        self.peering = None
        self.peer(network_stack=network_stack, peer_vpc=network_vpc)

        self.add_vpn()
        self.gui_dns_host = "gui"
        self.add_dns(namespace=self.dns_domain)

        # Create file system and volumes
        self.file_system = FbmFileSystem(
            scope=self,
            id="FileSystem",
            vpc=self.vpc
        )
        node_config_volume = self.file_system.create_volume(
            name="config", root_directory='/node/config', mount_dir="/config")
        node_data_volume = self.file_system.create_volume(
            name="data", root_directory='/node/data', mount_dir="/data")
        node_etc_volume = self.file_system.create_volume(
            name="etc", root_directory='/node/etc', mount_dir="/fedbiomed/etc")
        node_var_volume = self.file_system.create_volume(
            name="var", root_directory='/node/var', mount_dir="/fedbiomed/var")
        node_common_volume = self.file_system.create_volume(
            name="common", root_directory='/node/common',
            mount_dir="/fedbiomed/envs/common")

        mqtt_broker = network_stack.mqtt_broker
        mqtt_port = network_stack.mqtt_port
        uploads_url = network_stack.uploads_url

        self.data_sync = FbmDataSync(
            scope=self,
            id="DataSync",
            bucket_name=bucket_name,
            site_name=site_name,
            file_system=self.file_system.file_system,
            vpc=self.vpc,
            subnet_arn=f'arn:aws:ec2:{self.region}:{self.account}:subnet/{self.subnet_id}',
            region=self.region,
            account=self.account
        )

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
            vpc=self.vpc,
            cluster=self.cluster,
            cpu=4096,
            gpu_count=1,
            memory_limit_mib=30000,
            docker_image_asset=node_docker_image,
            task_name="node",
            file_system=self.file_system,
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
        self.gui_service = FargateService(
            scope=self,
            id="GuiService",
            web=True,
            cluster=self.cluster,
            dns_name=self.gui_dns_host,
            domain_zone=self.hosted_zone,
            cpu=4096,
            memory_limit_mib=30720,
            ephemeral_storage_gib=100,
            docker_image_asset=gui_docker_image,
            task_name="gui",
            container_port=8484,
            listener_port=8484,
            permitted_client_ip_range=self.cidr_range,
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": f"{mqtt_port}",
                "UPLOADS_URL": uploads_url},
            file_system=self.file_system,
            volumes=[node_data_volume, node_etc_volume, node_var_volume,
                     node_common_volume]
        )
        self.gui_service.load_balanced_service.target_group.configure_health_check(
            healthy_http_codes="200,304"
        )

        # Do this here after the stack has been created
        network_stack.open_peer_ports(self.cidr_range)

    def peer(self, network_stack: FbmNetworkStack, peer_vpc: ec2.Vpc):
        self.peering = ec2.CfnVPCPeeringConnection(
            self,
            "NodeNetworkPeer",
            vpc_id=self.vpc.vpc_id,
            peer_vpc_id=network_stack.vpc.vpc_id,
        )
        network_subnet_index = 0
        for subnet in network_stack.vpc.isolated_subnets:
            ec2.CfnRoute(
                self,
                f"NetworkNodeRoute{network_subnet_index}",
                destination_cidr_block=self.cidr_range,
                route_table_id=subnet.route_table.route_table_id,
                vpc_peering_connection_id=self.peering.ref,
            )
            network_subnet_index += 1
        subnet_index = 0
        for subnet in self.vpc.isolated_subnets:
            ec2.CfnRoute(
                self,
                f"NodeNetworkRoute{subnet_index}",
                destination_cidr_block=network_stack.cidr_range,
                route_table_id=subnet.route_table.route_table_id,
                vpc_peering_connection_id=self.peering.ref,
            )
            subnet_index += 1
        # Custom Construct to allow use of the peered VPC for DNS resolution
        AllowVPCPeeringDNSResolution(
            self,
            "peerConnectionDNSResolution",
            props=AllowVPCPeeringDNSResolutionProps(vpc_peering=self.peering))


class AllowVPCPeeringDNSResolutionProps:
    def __init__(self, vpc_peering: ec2.CfnVPCPeeringConnection):
        self.vpc_peering = vpc_peering


class AllowVPCPeeringDNSResolution(Construct):

    def __init__(self, scope: Construct, id: str,
                 props: AllowVPCPeeringDNSResolutionProps):
        super().__init__(scope, id)

        on_create = custom_resources.AwsSdkCall(
            service="EC2",
            action="modifyVpcPeeringConnectionOptions",
            parameters={
                "VpcPeeringConnectionId": props.vpc_peering.ref,
                "AccepterPeeringConnectionOptions": {
                    "AllowDnsResolutionFromRemoteVpc": True,
                },
                "RequesterPeeringConnectionOptions": {
                    "AllowDnsResolutionFromRemoteVpc": True
                }
            },
            physical_resource_id=custom_resources.PhysicalResourceId.of(
                'allowVPCPeeringDNSResolution:${props.vpcPeering.ref}'
            )
        )
        on_delete = custom_resources.AwsSdkCall(
            service="EC2",
            action="modifyVpcPeeringConnectionOptions",
            parameters={
                "VpcPeeringConnectionId": props.vpc_peering.ref,
                "AccepterPeeringConnectionOptions": {
                    "AllowDnsResolutionFromRemoteVpc": False,
                },
                "RequesterPeeringConnectionOptions": {
                    "AllowDnsResolutionFromRemoteVpc": False
                }
            }
        )

        custom_resource = custom_resources.AwsCustomResource(
            scope, "allow-peering-dns-resolution",
            policy=custom_resources.AwsCustomResourcePolicy.from_statements(
                statements=[
                    aws_iam.PolicyStatement(
                        effect=aws_iam.Effect.ALLOW,
                        resources=["*"],
                        actions=["ec2:ModifyVpcPeeringConnectionOptions"]
                    )
                ]),
            log_retention=logs.RetentionDays.ONE_DAY,
            on_create=on_create,
            on_update=on_create,
            on_delete=on_delete
        )
        custom_resource.node.add_dependency(props.vpc_peering)


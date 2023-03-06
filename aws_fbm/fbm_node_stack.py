from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.fbm_data_sync import FbmDataSync
from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.fbm_file_system import FbmFileSystem
from aws_fbm.utils import repo_path
from aws_cdk import (aws_ecs as ecs)
from aws_cdk import custom_resources, Environment
from aws_cdk import aws_ec2 as ec2, aws_iam

from constructs import Construct
import aws_cdk.aws_logs as logs
from aws_cdk.aws_ecr_assets import DockerImageAsset


class FbmNodeStack(FbmBaseStack):

    def __init__(self, scope: Construct, construct_id: str,
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
        self.add_dns(namespace=self.dns_domain)

        # Create file system and volumes
        self.file_system = FbmFileSystem(
            scope=self,
            id="FileSystem",
            vpc=self.vpc
        )
        node_config_volume = self.file_system.create_volume(
            name="config", root_directory='/node/config')
        node_data_volume = self.file_system.create_volume(
            name="data", root_directory='/node/data')
        node_etc_volume = self.file_system.create_volume(
            name="etc", root_directory='/node/etc')
        node_var_volume = self.file_system.create_volume(
            name="var", root_directory='/node/var')
        node_common_volume = self.file_system.create_volume(
            name="common", root_directory='/node/common')

        mqtt_broker = network_stack.mqtt_broker
        mqtt_broker_port = network_stack.mqtt_broker_port
        uploads_url = network_stack.uploads_url

        self.data_sync = FbmDataSync(
            self,
            "DataSync",
            bucket_name=bucket_name,
            stack_name=stack_name,
            volume=node_data_volume,
            file_system=self.file_system.file_system,
            vpc=self.vpc,
            subnet_arn=f'arn:aws:ec2:{self.region}:{self.account}:subnet/{self.subnet_id}',
            region=self.region,
            account=self.account
        )

        # Fed-BioMed Node service
        self.node_service_def = self.cluster.add_ec2_service_def(
            id="NodeServiceDef",
            dns_namespace=self.dns_namespace,
            dns_name="node",
            vpc=self.vpc,
            file_system=self.file_system
        )
        # Add volumes to node service
        self.node_service_def.add_volume(volume=node_config_volume)
        self.node_service_def.add_volume(volume=node_data_volume)
        self.node_service_def.add_volume(volume=node_etc_volume)
        self.node_service_def.add_volume(volume=node_var_volume)
        self.node_service_def.add_volume(volume=node_common_volume)

        # Docker image
        node_docker_image = DockerImageAsset(
            self,
            id="node",
            directory=str(repo_path() / "docker"),
            file="node/Dockerfile"
        )
        node_container = self.node_service_def.add_docker_container(
            node_docker_image,
            name="node",
            gpu_count=1,
            cpu=2048,
            memory_limit_mib=16384,
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": mqtt_broker_port,
                "UPLOADS_URL": uploads_url}
        )
        node_container.add_mount_points(
            ecs.MountPoint(
                source_volume=node_config_volume.volume_name,
                container_path="/config",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_data_volume.volume_name,
                container_path="/data",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_etc_volume.volume_name,
                container_path="/fedbiomed/etc",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_var_volume.volume_name,
                container_path="/fedbiomed/var",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_common_volume.volume_name,
                container_path="/fedbiomed/envs/common",
                read_only=False,
            )
        )
        # Create the node service
        self.node_service = self.node_service_def.create_service()

        # Note: We do not add permissions from the file storgae to the EC2
        # service here as we do for Fargate services,
        # as we instead add permissions to the EC2 security group

        # Fed-BioMed Gui service
        self.gui_service_def = self.cluster.add_fargate_service_def(
            id="GuiService",
            dns_namespace=self.dns_namespace,
            dns_name="gui",
            cpu=2048,
            memory_limit_mib=8192,
            ephemeral_storage_gib=40
        )
        # Add volumes to the task definition
        self.gui_service_def.add_volume(volume=node_data_volume)
        self.gui_service_def.add_volume(volume=node_etc_volume)
        self.gui_service_def.add_volume(volume=node_var_volume)
        self.gui_service_def.add_volume(volume=node_common_volume)
        # Docker image
        gui_docker_image = DockerImageAsset(
            self,
            id="gui",
            directory=str(repo_path() / "docker"),
            file="gui/Dockerfile"
        )
        gui_container = self.gui_service_def.add_docker_container(
            gui_docker_image,
            name="gui",
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": mqtt_broker_port,
                "UPLOADS_URL": uploads_url},
            cpu=2048,
            memory_limit_mib=8192
        )
        gui_container.add_port_mappings(
            ecs.PortMapping(container_port=8484))
        gui_container.add_mount_points(
            ecs.MountPoint(
                source_volume=node_data_volume.volume_name,
                container_path="/data",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_etc_volume.volume_name,
                container_path="/fedbiomed/etc",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_var_volume.volume_name,
                container_path="/fedbiomed/var",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_common_volume.volume_name,
                container_path="/fedbiomed/envs/common",
                read_only=False,
            ),
        )
        # Create the gui service
        self.gui_service = self.gui_service_def.create_service()
        # Allow the gui service to access EFS
        self.file_system.allow_access_from_service(self.gui_service)
        # Allow incoming connections to gui
        for port in [8484]:
            self.gui_service.connections.security_groups[0].add_ingress_rule(
                peer=ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
                connection=ec2.Port.tcp(port),
                description=f"Allow http inbound from VPC on port {port}"
            )

        # Do this here after the stack has been created
        self.open_peer_ports(network_stack=network_stack)

    def peer(self, network_stack: FbmNetworkStack, peer_vpc: ec2.Vpc):
        self.peering = ec2.CfnVPCPeeringConnection(
            self,
            "NodeNetworkPeer",
            vpc_id=self.vpc.vpc_id,
            peer_vpc_id=network_stack.vpc.vpc_id,
        )
        ec2.CfnRoute(
            self,
            "NetworkNodeRoute",
            destination_cidr_block=self.cidr_range,
            route_table_id=network_stack.vpc.isolated_subnets[0].route_table.route_table_id,
            vpc_peering_connection_id=self.peering.ref,
        )
        ec2.CfnRoute(
            self,
            "NodeNetworkRoute",
            destination_cidr_block=network_stack.cidr_range,
            route_table_id=self.vpc.isolated_subnets[0].route_table.route_table_id,
            vpc_peering_connection_id=self.peering.ref,
        )
        # Custom Construct to allow use of the peered VPC for DNS resolution
        AllowVPCPeeringDNSResolution(
            self,
            "peerConnectionDNSResolution",
            props=AllowVPCPeeringDNSResolutionProps(vpc_peering=self.peering))

    def open_peer_ports(self, network_stack: FbmNetworkStack):
        network_stack.network_service.connections.allow_from(
            ec2.Peer.ipv4(self.cidr_range), ec2.Port.tcp(1883))
        network_stack.network_service.connections.allow_from(
            ec2.Peer.ipv4(self.cidr_range), ec2.Port.tcp(8000))


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


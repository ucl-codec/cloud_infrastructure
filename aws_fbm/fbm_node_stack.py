from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.utils import repo_path
from aws_cdk import (aws_ecs as ecs)
from aws_cdk import custom_resources, Environment
from aws_cdk import aws_ec2 as ec2, aws_iam
from aws_cdk import aws_s3
from constructs import Construct
import aws_cdk.aws_logs as logs


class FbmNodeStack(FbmBaseStack):

    def __init__(self, scope: Construct, construct_id: str,
                 stack_name: str,
                 stack_prefix: str,
                 description: str,
                 network_number: int,
                 network_stack: FbmNetworkStack,
                 network_vpc: ec2.Vpc,
                 env: Environment) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         stack_prefix=stack_prefix,
                         description=description,
                         network_number=network_number,
                         cpu=8192,
                         memory_limit_mib=40960,
                         env=env)
        self.peering = None
        self.peer(network_stack=network_stack, peer_vpc=network_vpc)

        self.add_vpn()
        self.add_dns(namespace="passian.clinical")

        self.add_file_system()
        node_config_volume_name = self.add_volume(
            name="config", root_directory='/node/config')
        node_data_volume_name = self.add_volume(
            name="data", root_directory='/node/data')
        node_etc_volume_name = self.add_volume(
            name="etc", root_directory='/node/etc')
        node_var_volume_name = self.add_volume(
            name="var", root_directory='/node/var')
        node_common_volume_name = self.add_volume(
            name="common", root_directory='/node/common')

        mqtt_broker = "researcher.passian.federated"
        mqtt_broker_port = "1883"
        uploads_url = "http://researcher.passian.federated:8000/upload/"

        # Node container
        node_container = self.add_docker_container(
            name="node",
            context_dir=str(repo_path() / "docker"),
            path_to_dockerfile="node/Dockerfile",
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": mqtt_broker_port,
                "UPLOADS_URL": uploads_url}
        )
        node_container.add_mount_points(
            ecs.MountPoint(
                source_volume=node_config_volume_name,
                container_path="/config",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_data_volume_name,
                container_path="/data",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_etc_volume_name,
                container_path="/fedbiomed/etc",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_var_volume_name,
                container_path="/fedbiomed/var",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_common_volume_name,
                container_path="/fedbiomed/envs/common",
                read_only=False,
            )
        )

        # Gui container
        gui_container = self.add_docker_container(
            name="gui",
            context_dir=str(repo_path() / "docker"),
            path_to_dockerfile="gui/Dockerfile",
            environment={
                "MQTT_BROKER": mqtt_broker,
                "MQTT_BROKER_PORT": mqtt_broker_port,
                "UPLOADS_URL": uploads_url}
        )
        gui_container.add_port_mappings(
            ecs.PortMapping(container_port=8484))
        gui_container.add_mount_points(
            ecs.MountPoint(
                source_volume=node_data_volume_name,
                container_path="/data",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_etc_volume_name,
                container_path="/fedbiomed/etc",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_var_volume_name,
                container_path="/fedbiomed/var",
                read_only=False,
            ),
            ecs.MountPoint(
                source_volume=node_common_volume_name,
                container_path="/fedbiomed/envs/common",
                read_only=False,
            ),
        )

        self.add_service(dns_name="node", ports=[8484])

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
        network_stack.fargate_service.connections.allow_from(
            ec2.Peer.ipv4(self.cidr_range), ec2.Port.tcp(1883))
        network_stack.fargate_service.connections.allow_from(
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

from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.fbm_data_sync import FbmDataSync
from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.fbm_file_system import FbmFileSystem
from aws_fbm.constructs.allow_peering_dns_resolution import \
    AllowVPCPeeringDNSResolution

from aws_cdk import Environment
from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class FbmNodeStack(FbmBaseStack):

    def __init__(self, scope: Construct, construct_id: str,
                 stack_name: str,
                 site_name: str,
                 dns_domain: str,
                 description: str,
                 network_number: int,
                 bucket_name: str,
                 network_stack: FbmNetworkStack,
                 network_vpc: ec2.Vpc,
                 env: Environment) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         site_name=site_name,
                         dns_domain=dns_domain,
                         description=description,
                         network_number=network_number,
                         env=env)

        # Create file system and volumes for node stack
        self.file_system = FbmFileSystem(
            scope=self,
            id="FileSystem",
            vpc=self.vpc
        )

        # Set up DataSync from S3 bucket to EFS node storage
        self.data_sync = FbmDataSync(
            scope=self,
            id="DataSync",
            bucket_name=bucket_name,
            site_name=site_name,
            file_system=self.file_system.file_system,
            vpc=self.vpc,
            subnet_arn=f'arn:aws:ec2:{self.region}:{self.account}:'
                       f'subnet/{self.first_subnet_id}',
            region=self.region,
            account=self.account
        )

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
            vpc_peering=self.peering)

        # Allow the node VPC to resolve DNS names from the network's hosted zone
        # network_stack.hosted_zone.add_vpc(self.vpc)

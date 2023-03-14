from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.stacks.network_service_stack import NetworkServiceStack
from aws_fbm.fbm_node_stack import FbmNodeStack
from aws_fbm.fbm_constructs.allow_peering_dns_resolution import \
    AllowVPCPeeringDNSResolution

from aws_cdk import Environment, Stack
from aws_cdk import aws_ec2 as ec2
from constructs import Construct

from typing import List


class PeeringStack(Stack):
    """CDK stack defining peering between FBM network and node VPCs"""

    def __init__(self, scope: Construct, id: str,
                 network_stack: FbmNetworkStack,
                 network_service_stack: NetworkServiceStack,
                 node_stacks: List[FbmNodeStack],
                 env: Environment) -> None:
        super().__init__(scope, id=id,
                         description=f"FBM peering stack",
                         env=env)

        # Peer each node
        for node_stack in node_stacks:
            # Peer the VPCs and add routes
            self.peer(network=network_stack, node=node_stack)

            # Open network services to the node service
            network_service_stack.allow_from_ip_range(node_stack.cidr_range)

            # Allow node VPC to resolve DNS names from the network's hosted zone
            network_stack.hosted_zone.add_vpc(node_stack.vpc)

    def peer(self, network: FbmNetworkStack, node: FbmNodeStack):
        peering = ec2.CfnVPCPeeringConnection(
            self,
            f"Peer{network.stack_name}{node.stack_name}",
            vpc_id=node.vpc.vpc_id,
            peer_vpc_id=network.vpc.vpc_id,
        )
        for index, subnet in enumerate(network.vpc.isolated_subnets):
            ec2.CfnRoute(
                self,
                f"Route{network.stack_name}{node.stack_name}{index}",
                destination_cidr_block=node.cidr_range,
                route_table_id=subnet.route_table.route_table_id,
                vpc_peering_connection_id=peering.ref,
            )
        for index, subnet in enumerate(node.vpc.isolated_subnets):
            ec2.CfnRoute(
                self,
                f"Route{node.stack_name}{network.stack_name}{index}",
                destination_cidr_block=network.cidr_range,
                route_table_id=subnet.route_table.route_table_id,
                vpc_peering_connection_id=peering.ref,
            )

        # Custom Construct to allow use of the peered VPC for DNS resolution
        AllowVPCPeeringDNSResolution(
            self,
            f"PeerConnectionDNSResolution{node.stack_name}",
            vpc_peering=peering)

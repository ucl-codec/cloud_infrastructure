from aws_cdk import Environment
from aws_cdk import Stack

from constructs import Construct
from aws_cdk import aws_ec2 as ec2
import aws_cdk.aws_ssm as ssm
from aws_cdk import aws_route53 as route53


class FbmBaseStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, *,
                 stack_name: str,
                 description: str,
                 network_number: int,
                 env: Environment) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         description=description,
                         env=env)

        self.cidr_range = f"10.{2*network_number}.0.0/16"
        self.vpn_cidr_range = f"10.{2*network_number + 1}.0.0/22"
        self.dns_ip = f"10.{2*network_number}.0.2"
        self.vpn_cert_arn = ssm.StringParameter.value_for_string_parameter(
            self, "passian-fbm-vpn-server-cert-arn")

        # Create VPC
        self.vpc = ec2.Vpc(
            self,
            "VPC",
            # S3 gateway is required to use the ECR because we are using
            # a private subnet with no internet connectivity
            gateway_endpoints={
                "S3": ec2.GatewayVpcEndpointOptions(
                    service=ec2.GatewayVpcEndpointAwsService.S3
                )
            },
            ip_addresses=ec2.IpAddresses.cidr(self.cidr_range),
            nat_gateways=0,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=2,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name="private",
                    cidr_mask=24,
                    subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)]
            )
        self.first_subnet_id = self.vpc.select_subnets(subnet_group_name="private").subnet_ids[0]

        # These endpoints are required in order to use the ECS
        # because we are using a private subnet with no internet connectivity
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="AgentEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECS_AGENT)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="TelemetryEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECS_TELEMETRY)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="EcsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECS)

        # These endpoints are required in order to use the ECR and logging
        # because we are using a private subnet with no internet connectivity
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="ECRDockerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="ECREndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="CloudWatchEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="CloudWatchLogsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="CloudWatchEventsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="SSMEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SSM)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="Ec2MessagesEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES)
        self.add_interface_endpoint(
            vpc=self.vpc,
            name="SSMMessagesEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES)

        self.vpn_endpoint = None

    def add_dns(self, namespace):
        self.hosted_zone = route53.HostedZone(
            self,
            "HostedZone",
            vpcs=[self.vpc],
            zone_name=namespace,
            comment="Private Hosted Zone for FBM"
        )

    def add_vpn(self):
        """Add VPN endpoint"""

        self.vpn_endpoint = self.vpc.add_client_vpn_endpoint(
            "VpnEndpoint",
            cidr=self.vpn_cidr_range,
            server_certificate_arn=self.vpn_cert_arn,
            # ToDo: change this to an authorisation rule that restricts access
            # to a subnet which just corresponds to the GUI/researcher
            authorize_all_users_to_vpc_cidr=True,  # Automatically creates authorization rule
            client_certificate_arn=self.vpn_cert_arn,
            self_service_portal=False,
            split_tunnel=True,
            dns_servers=[self.dns_ip],
            description=f"{self.stack_name} Client VPN Endpoint",
            # vpc_subnets=""
        )

    def add_interface_endpoint(self, vpc, name, service):
        endpoint = self.vpc.add_interface_endpoint(id=name, service=service)
        endpoint.connections.allow_from(ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
                                        endpoint.connections.default_port)


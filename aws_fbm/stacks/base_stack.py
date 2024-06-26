from aws_cdk import Environment, Stack
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ssm as ssm
from aws_cdk import aws_route53 as route53
from constructs import Construct

from typing import Optional


class BaseStack(Stack):
    """CDK stack base class defining common VPC, VPN and DNS configuration for
    FBM network and node stacks"""

    def __init__(self, scope: Construct, id: str,
                 site_description: str,
                 dns_domain: str,
                 parent_dns_domain: Optional[str],
                 description: str,
                 network_number: int,
                 use_https: bool,
                 param_vpn_cert_arn: str,
                 param_vpn_endpoint_id: str,
                 env: Environment) -> None:
        super().__init__(scope=scope, id=id,
                         description=description,
                         env=env,
                         termination_protection=True)

        self.site_description = site_description
        self.dns_domain = dns_domain
        self.use_https = use_https

        # Select IP ranges for VPC and VPN. These must be non-overlapping
        # across the entire system, since the VPCs are peered
        self.cidr_range = f"10.{2*network_number}.0.0/16"
        self.vpn_cidr_range = f"10.{2*network_number + 1}.0.0/22"
        self.dns_ip = f"10.{2*network_number}.0.2"
        self.vpn_cert_arn = ssm.StringParameter.value_for_string_parameter(
            scope=self, parameter_name=param_vpn_cert_arn)

        self.add_vpc()

        # Some resources must be created in a specific subnet, so we
        # arbitrarily choose the first
        self.first_subnet_id = self.vpc.select_subnets(
            subnet_group_name="private").subnet_ids[0]
        self.add_vpn(param_vpn_endpoint_id=param_vpn_endpoint_id)
        self.add_dns(namespace=self.dns_domain,
                     parent_namespace=parent_dns_domain)

    def add_vpc(self):
        """Create VPC"""

        # S3 gateway is required to use the ECR because we are using
        # a private subnet with no internet connectivity
        self.vpc = ec2.Vpc(
            self,
            "VPC",
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

        # These endpoints are required in order to use the ECS
        # because we are using a private subnet with no internet connectivity
        self.add_interface_endpoint(
            name="AgentEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECS_AGENT)
        self.add_interface_endpoint(
            name="TelemetryEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECS_TELEMETRY)
        self.add_interface_endpoint(
            name="EcsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECS)

        # These endpoints are required in order to use the ECR and logging
        # because we are using a private subnet with no internet connectivity
        self.add_interface_endpoint(
            name="ECRDockerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR_DOCKER)
        self.add_interface_endpoint(
            name="ECREndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.ECR)
        self.add_interface_endpoint(
            name="CloudWatchEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH)
        self.add_interface_endpoint(
            name="CloudWatchLogsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_LOGS)
        self.add_interface_endpoint(
            name="CloudWatchEventsEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH_EVENTS)
        self.add_interface_endpoint(
            name="SSMEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SSM)
        self.add_interface_endpoint(
            name="Ec2MessagesEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.EC2_MESSAGES)
        self.add_interface_endpoint(
            name="SSMMessagesEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SSM_MESSAGES)

        # Endpoints for passing AWS Secrets to ECS containers
        self.add_interface_endpoint(
            name="SecretsManagerEndpoint",
            service=ec2.InterfaceVpcEndpointAwsService.SECRETS_MANAGER)

    def add_dns(self, namespace: str, parent_namespace: Optional[str]):
        # Create the public hosted zone. This is only used in validating
        # certificates for https
        self.public_hosted_zone = route53.HostedZone(
            self,
            "PublicHostedZone",
            zone_name=namespace,
            comment=f"Public Hosted Zone for {self.site_description}, used"
                    f"for certificate validation"
        )

        if parent_namespace:
            # Access the parent public hosted zone - this must already exist
            parent_public_hosted_zone = route53.HostedZone.from_lookup(
                scope=self,
                id="ParentPublicHostedZone",
                domain_name=parent_namespace,
                private_zone=False
            )
            # Create the NS records that route public traffic from the parent
            # public zone to the public zone. This is only used to validate the
            # https certificates
            parent_ns_records = route53.NsRecord(
                scope=self,
                id="NsRecords",
                zone=parent_public_hosted_zone,
                comment=f"NS records for {self.public_hosted_zone}",
                delete_existing=True,
                record_name=namespace,
                values=self.public_hosted_zone.hosted_zone_name_servers
            )

        # Create the private hosted zone used to access the services
        self.hosted_zone = route53.HostedZone(
            self,
            "PrivateHostedZone",
            vpcs=[self.vpc],
            zone_name=namespace,
            comment=f"Private Hosted Zone for {self.site_description}"
        )

    def add_vpn(self, param_vpn_endpoint_id: str):
        """Add VPN endpoint"""

        # Note this will automatically create authorization rule
        self.vpn_endpoint = self.vpc.add_client_vpn_endpoint(
            "VpnEndpoint",
            cidr=self.vpn_cidr_range,
            server_certificate_arn=self.vpn_cert_arn,
            authorize_all_users_to_vpc_cidr=True,
            client_certificate_arn=self.vpn_cert_arn,
            self_service_portal=False,
            split_tunnel=True,
            dns_servers=[self.dns_ip],
            description=f"{self.stack_name} Client VPN Endpoint",
        )
        self.vpn_endpoint_id_param = ssm.StringParameter(
            scope=self,
            id="VpnEndpointIdParam",
            parameter_name=param_vpn_endpoint_id,
            string_value=self.vpn_endpoint.endpoint_id
        )

    def add_interface_endpoint(self, name, service):
        endpoint = self.vpc.add_interface_endpoint(id=name, service=service)
        endpoint.connections.allow_from(ec2.Peer.ipv4(self.vpc.vpc_cidr_block),
                                        endpoint.connections.default_port)


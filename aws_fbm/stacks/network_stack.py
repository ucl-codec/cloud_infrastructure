from aws_fbm.stacks.base_stack import BaseStack
from aws_fbm.fbm_constructs.file_system import FileSystem
from aws_fbm.utils.config import NetworkConfig

from aws_cdk import Environment
from constructs import Construct


class NetworkStack(BaseStack):
    """CDK stack defining the core configuration for the FBM network
    component. This defines stateful configuration such as VPC, VPN and
    the file system.
    """

    def __init__(self, scope: Construct,
                 network_config: NetworkConfig,
                 env: Environment) -> None:
        super().__init__(
            scope=scope,
            id=f"{network_config.name_prefix}NetworkStack",
            description=f"FBM network stack for "
                        f"{network_config.site_description}",
            site_description=network_config.site_description,
            dns_domain=network_config.domain_name,
            network_number=0,
            param_vpn_cert_arn=network_config.param_vpn_cert_arn,
            env=env
        )
        self.name_prefix = network_config.name_prefix

        # Create file system and volumes for researcher stack
        self.file_system = FileSystem(
            scope=self,
            id="FileSystem",
            vpc=self.vpc
        )

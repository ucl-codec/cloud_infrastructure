from aws_fbm.stacks.base_stack import BaseStack
from aws_fbm.fbm_constructs.file_system import FileSystem

from aws_cdk import Environment
from constructs import Construct


class NetworkStack(BaseStack):
    """CDK stack defining the core configuration for the FBM network
    component. This defines stateful configuration such as VPC, VPN and
    the file system.
    """

    def __init__(self, scope: Construct, id: str,
                 site_name: str,
                 dns_domain: str,
                 network_number: int,
                 env: Environment) -> None:
        super().__init__(scope=scope, id=id,
                         description=f"FBM network stack for {site_name}",
                         site_name=site_name,
                         dns_domain=dns_domain,
                         network_number=network_number,
                         env=env)

        # Create file system and volumes for researcher stack
        self.file_system = FileSystem(
            scope=self,
            id="FileSystem",
            vpc=self.vpc
        )

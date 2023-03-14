from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.fbm_constructs.file_system import FileSystem

from constructs import Construct


class FbmNetworkStack(FbmBaseStack):
    """CDK stack defining the core configuration for the FBM network
    component. This defines stateful configuration such as VPC, VPN and
    the file system.
    """

    def __init__(self, scope: Construct, id: str,
                 site_name: str,
                 dns_domain: str,
                 description: str,
                 network_number: int,
                 **kwargs) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         site_name=site_name,
                         dns_domain=dns_domain,
                         description=description,
                         network_number=network_number,
                         **kwargs)

        # Create file system and volumes for researcher stack
        self.file_system = FileSystem(
            scope=self,
            id="FileSystem",
            vpc=self.vpc
        )

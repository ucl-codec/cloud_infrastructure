from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.fbm_file_system import FbmFileSystem

from constructs import Construct


class FbmNetworkStack(FbmBaseStack):

    def __init__(self, scope: Construct, construct_id: str,
                 stack_name: str,
                 site_name: str,
                 dns_domain: str,
                 description: str,
                 network_number: int,
                 **kwargs) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         description=description,
                         network_number=network_number,
                         **kwargs)

        self.site_name = site_name
        self.dns_domain = dns_domain
        self.add_vpn()

        # Create file system and volumes
        self.file_system = FbmFileSystem(
            scope=self,
            id="FileSystem",
            vpc=self.vpc
        )

        self.add_dns(namespace=self.dns_domain)


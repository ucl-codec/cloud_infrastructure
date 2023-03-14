from aws_fbm.fbm_base_stack import FbmBaseStack
from aws_fbm.fbm_constructs.data_sync import DataSync
from aws_fbm.fbm_constructs.file_system import FileSystem
from aws_cdk import Environment

from constructs import Construct


class FbmNodeStack(FbmBaseStack):

    def __init__(self, scope: Construct, construct_id: str,
                 stack_name: str,
                 site_name: str,
                 dns_domain: str,
                 description: str,
                 network_number: int,
                 bucket_name: str,
                 env: Environment) -> None:
        super().__init__(scope, construct_id,
                         stack_name=stack_name,
                         site_name=site_name,
                         dns_domain=dns_domain,
                         description=description,
                         network_number=network_number,
                         env=env)

        # Create file system and volumes for node stack
        self.file_system = FileSystem(
            scope=self,
            id="FileSystem",
            vpc=self.vpc
        )

        # Set up DataSync from S3 bucket to EFS node storage
        self.data_sync = DataSync(
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

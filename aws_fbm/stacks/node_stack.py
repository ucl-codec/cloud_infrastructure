
from aws_fbm.stacks.base_stack import BaseStack
from aws_fbm.fbm_constructs.data_sync import DataSync
from aws_fbm.fbm_constructs.file_system import FileSystem
from aws_cdk import Environment

from constructs import Construct

from typing import Optional


class NodeStack(BaseStack):
    """CDK stack defining the core configuration for the FBM network
    component. This defines stateful configuration such as the file system.
    """

    def __init__(self, scope: Construct,
                 name_prefix: str,
                 site_name: str,
                 dns_domain: str,
                 network_number: int,
                 bucket_name: str,
                 env: Environment,
                 stack_name: Optional[str] = None) -> None:
        stack_name = stack_name or f"{name_prefix}NodeStack"
        super().__init__(scope=scope, id=stack_name,
                         site_name=site_name,
                         description=f"FBM node stack for {site_name}",
                         dns_domain=dns_domain,
                         network_number=network_number,
                         env=env)
        self.name_prefix = name_prefix

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

from aws_fbm.stacks.base_stack import BaseStack
from aws_fbm.fbm_constructs.data_sync import DataSync
from aws_fbm.fbm_constructs.file_system import FileSystem
from aws_fbm.utils.config import NodeConfig

from aws_cdk import Environment
from constructs import Construct


class NodeStack(BaseStack):
    """CDK stack defining the core configuration for the FBM network
    component. This defines stateful configuration such as the file system.
    """

    def __init__(self, scope: Construct,
                 node_config: NodeConfig,
                 network_number: int,
                 env: Environment) -> None:
        # Stack name is derived fom name_prefix, but can be overridden in the
        # configuration if required
        stack_name = node_config.stack_name or \
                     f"{node_config.name_prefix}-NodeStack"
        super().__init__(
            scope=scope,
            id=stack_name,
            site_description=node_config.site_description,
            description=f"FBM node stack for {node_config.site_description}",
            dns_domain=node_config.domain_name,
            network_number=network_number,
            param_vpn_cert_arn=node_config.param_vpn_cert_arn,
            param_vpn_endpoint_id=node_config.param_vpn_endpoint_id,
            env=env
        )
        self.name_prefix = node_config.name_prefix

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
            bucket_name=node_config.bucket_name,
            site_description=node_config.site_description,
            file_system=self.file_system.file_system,
            vpc=self.vpc,
            subnet_arn=f'arn:aws:ec2:{self.region}:{self.account}:'
                       f'subnet/{self.first_subnet_id}',
            region=self.region,
            account=self.account
        )

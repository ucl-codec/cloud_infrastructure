from aws_fbm.utils.config import NodeConfig
from aws_cdk import aws_s3 as s3
from aws_cdk import Environment, Stack
from constructs import Construct


class DataImportStack(Stack):
    """CDK stack defining an S3 bucket for importing data into PassianFL"""

    def __init__(self, scope: Construct,
                 node_config: NodeConfig,
                 env: Environment):
        super().__init__(scope=scope,
                         id=f"{node_config.name_prefix}DataImportStack",
                         description=f"FBM data import stack for "
                                     f"{node_config.site_description}",
                         env=env)

        # Create S3 bucket for data import
        self.import_bucket = s3.Bucket(
            self,
            "DataImportBucket",
            bucket_name=f"{node_config.import_bucket_name}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            enforce_ssl=True,
            versioned=False,
            access_control=s3.BucketAccessControl.PRIVATE
        )

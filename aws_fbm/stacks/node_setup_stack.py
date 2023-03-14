from constructs import Construct
from aws_cdk import aws_s3 as s3
from aws_cdk import Environment
from aws_cdk import Stack


class NodeSetupStack(Stack):
    """CDK stack defining persistent resources for the clinical node sites
    which may need to persist beyond the lifetime of the NodeStack, such as the
    S3 bucket
    """

    def __init__(self, scope: Construct,
                 name_prefix: str,
                 site_name: str,
                 bucket_name: str,
                 env: Environment):
        super().__init__(scope=scope,
                         id=f"{name_prefix}SetupStack",
                         description=f"FBM setup stack for site {site_name}",
                         env=env)

        # Create S3 bucket for data import
        self.import_bucket = s3.Bucket(
            self,
            "NodeImportBucket",
            bucket_name=f"{bucket_name}",
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            enforce_ssl=True,
            versioned=False,
            access_control=s3.BucketAccessControl.PRIVATE
        )

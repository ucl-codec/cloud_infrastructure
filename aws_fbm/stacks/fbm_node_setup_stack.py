from aws_cdk import Stack
from constructs import Construct
from aws_cdk import aws_s3 as s3


class FbmNodeSetupStack(Stack):
    def __init__(self,
                 scope: Construct,
                 id: str,
                 site_name: str,
                 bucket_name: str):
        super().__init__(scope, id=id,
                         description=f"FBM setup stack for site {site_name}")

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

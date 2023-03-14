import aws_cdk as cdk

from pathlib import Path
import os


def repo_path() -> Path:
    """Return path to repository root"""
    return Path(__file__).parent.parent.parent.resolve()


def get_environment() -> cdk.Environment:
    """Fetch account and region from env vars"""
    return cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                           region=os.getenv('CDK_DEFAULT_REGION'))

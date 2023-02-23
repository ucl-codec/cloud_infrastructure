#!/usr/bin/env python3

import os

import aws_cdk as cdk
from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.fbm_node_stack import FbmNodeStack


def get_environment() -> cdk.Environment:
    # Fetch account and region from env vars.
    return cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                           region=os.getenv('CDK_DEFAULT_REGION'))


app = cdk.App()
network = FbmNetworkStack(
    scope=app,
    construct_id="FbmNetworkStack",
    env=get_environment()
)
node = FbmNodeStack(
    scope=app,
    construct_id="FbmNodeStack",
    network_stack=network,
    network_vpc=network.vpc,
    env=get_environment()

)


app.synth()

#!/usr/bin/env python3

import os

import aws_cdk as cdk

from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.fbm_node_stack import FbmNodeStack

vpn_cert_arn = "ADD-IN-ART-FOR-CERT"  # ToDo: fetch from parameter store

app = cdk.App()
network = FbmNetworkStack(
    scope=app,
    construct_id="FbmNetworkStack",
    vpn_cert_arn=vpn_cert_arn,
    # Fetch account and region from env vars.
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                        region=os.getenv('CDK_DEFAULT_REGION')),
)
node = FbmNodeStack(
    scope=app,
    construct_id="FbmNodeStack",
    vpn_cert_arn=vpn_cert_arn,
    network_stack=network,
    network_vpc=network.vpc,

    # Fetch account and region from env vars.
    env=cdk.Environment(account=os.getenv('CDK_DEFAULT_ACCOUNT'),
                        region=os.getenv('CDK_DEFAULT_REGION')),
)


app.synth()

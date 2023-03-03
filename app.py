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
    stack_name="FbmNetworkStack",
    dns_domain="passian.federated",
    description="PASSIAN Fed-BioMed stack for federation network",
    network_number=0,
    env=get_environment()
)

node_a = FbmNodeStack(
    scope=app,
    construct_id="FbmNodeStackA",
    stack_name="FbmNodeStackA",
    dns_domain="passian.clinicala",
    bucket_name="clinical-node-a",
    description="PASSIAN Fed-BioMed stack for clinical node A",
    network_number=1,
    network_stack=network,
    network_vpc=network.vpc,
    env=get_environment()
)

node_b = FbmNodeStack(
    scope=app,
    construct_id="FbmNodeStackB",
    stack_name="FbmNodeStackB",
    dns_domain="passian.clinicalb",
    bucket_name="clinical-node-b",
    description="PASSIAN Fed-BioMed stack for clinical node B",
    network_number=2,
    network_stack=network,
    network_vpc=network.vpc,
    env=get_environment()
)


app.synth()

#!/usr/bin/env python3

import os

import aws_cdk as cdk
from aws_fbm.fbm_network_stack import FbmNetworkStack
from aws_fbm.fbm_node_stack import FbmNodeStack
from aws_fbm.stacks.fbm_node_setup_stack import FbmNodeSetupStack


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

node_a_import_bucket_name = "clinical-node-a-import-bucket"
node_a_setup = FbmNodeSetupStack(
    scope=app, id="FbmNodeStackA", site_name="Clinical Node A",
    bucket_name=node_a_import_bucket_name)
node_a = FbmNodeStack(
    scope=app,
    construct_id="FbmNodeStackA",
    site_name = "Clinical Node A",
    stack_name="FbmNodeStackA",
    dns_domain="passian.clinicala",
    bucket_name=node_a_import_bucket_name,
    description="PASSIAN Fed-BioMed stack for clinical node A",
    network_number=1,
    network_stack=network,
    network_vpc=network.vpc,
    env=get_environment()
)

node_b_import_bucket_name = "clinical-node-b-import-bucket"
node_b_setup = FbmNodeSetupStack(
    scope=app, id="FbmNodeStackB", site_name="Clinical Node B",
    bucket_name=node_b_import_bucket_name)
node_b = FbmNodeStack(
    scope=app,
    construct_id="FbmNodeStackB",
    site_name = "Clinical Node B",
    stack_name="FbmNodeStackB",
    dns_domain="passian.clinicalb",
    bucket_name=node_b_import_bucket_name,
    description="PASSIAN Fed-BioMed stack for clinical node B",
    network_number=2,
    network_stack=network,
    network_vpc=network.vpc,
    env=get_environment()
)


app.synth()

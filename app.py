#!/usr/bin/env python3

from aws_fbm.stacks.network_stack import NetworkStack
from aws_fbm.stacks.node_stack import NodeStack
from aws_fbm.stacks.peering_stack import PeeringStack
from aws_fbm.stacks.node_service_stack import NodeServiceStack
from aws_fbm.stacks.network_service_stack import NetworkServiceStack
from aws_fbm.stacks.researcher_service_stack import ResearcherServiceStack
from aws_fbm.utils.config import read_config_file
from aws_fbm.utils.utils import get_environment

import aws_cdk as cdk


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

# For initial setup
# node_a_setup = FbmNodeSetupStack(
#     scope=app, id="FbmNodeASetup", site_name="Clinical Node A",
#     bucket_name=node_a_import_bucket_name)

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

# For initial setup
# node_b_setup = FbmNodeSetupStack(
#     scope=app, id="FbmNodeBSetup", site_name="Clinical Node B",
#     bucket_name=node_b_import_bucket_name)

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



# test_network = FbmNetworkStack(
#     scope=app,
#     construct_id="TestNetworkStack",
#     stack_name="TestNetworkStack",
#     dns_domain="test.testfederated2",
#     description="Test PASSIAN Fed-BioMed stack for federation network",
#     network_number=0,
#     env=get_environment()
# )
#
# test_node_a_import_bucket_name = "test-a-import-bucket"
# # test_node_a_setup = FbmNodeSetupStack(
# #     scope=app, id="TestNodeASetup", site_name="Test A",
# #     bucket_name=test_node_a_import_bucket_name)
#
# test_node_a = FbmNodeStack(
#     scope=app,
#     construct_id="TestNodeStackA",
#     site_name="Test Node A",
#     stack_name="TestNodeStackA",
#     dns_domain="test.testclinicala2",
#     bucket_name=test_node_a_import_bucket_name,
#     description="Test PASSIAN Fed-BioMed stack for clinical node A",
#     network_number=1,
#     network_stack=test_network,
#     network_vpc=test_network.vpc,
#     env=get_environment()
# )

app.synth()

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


# Create the app, the base construct on which all the stacks are build
app = cdk.App()

# Get the config context parameter and use it to read a config file
# The context is provided on the cdk command line, e.g. --context config=dev
# This corresponds to a config file to be read, e.g. config/dev.cfg
config_name = app.node.try_get_context("config")
config = read_config_file(config_name)

# Create stateful federated stack for hold network and researcher services
network_stack = NetworkStack(
    scope=app,
    network_config=config.network,
    env=get_environment()
)

# Create stack for network services
network_service_stack = NetworkServiceStack(
    scope=app,
    network_stack=network_stack,
    env=get_environment()
)

# Create stack for researcher services
researcher_service_stack = ResearcherServiceStack(
    scope=app,
    network_stack=network_stack,
    network_service_stack=network_service_stack,
    env=get_environment()
)

# Iterate through nodes from configuration
nodes = []
for index, node in enumerate(config.nodes):

    # Create stateful S3 bucket stack
    # Comment out if using a pre-existing S3 bucket
    # node_setup = NodeSetupStack(
    #     scope=app,
    #     name_prefix=node.name_prefix,
    #     site_name=node.site_name,
    #     bucket_name=node.bucket_name,
    #     env=get_environment()
    # )

    # Create stateful node stack
    node_stack = NodeStack(
        scope=app,
        node_config=node,
        network_number=index+1,
        env=get_environment()
    )
    # Create node services stack
    node_service_stack = NodeServiceStack(
        scope=app,
        node_stack=node_stack,
        node_config=node,
        env=get_environment(),
        mqtt_broker=network_service_stack.mqtt_broker,
        mqtt_port=network_service_stack.mqtt_port,
        uploads_url=network_service_stack.uploads_url,
    )
    nodes.append(node_stack)

# Create peering stack which connects network and node stacks
peering_stack = PeeringStack(
    scope=app,
    network_stack=network_stack,
    network_service_stack=network_service_stack,
    node_stacks=nodes,
    env=get_environment()
)

app.synth()

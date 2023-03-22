#!/bin/bash

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))

# Start from repo dir
cd "${REPO_DIR}"

# Update test stacks
cdk deploy --all --profile passian --context config=dev
#cdk deploy TestNetworkStack TestNetworkServiceStack TestResearcherServiceStack TestNodeStackA TestNodeServiceStackA TestPeeringStack --profile passian --context config=dev

# Full deployment
#cdk deploy TestNetworkStack TestNodeASetup TestNodeStackA --profile passian

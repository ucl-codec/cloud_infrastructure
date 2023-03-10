#!/bin/bash

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))

# Start from repo dir
cd "${REPO_DIR}"

# Deploy main stacks
cdk deploy FbmNetworkStack FbmNodeStackA FbmNodeStackB --profile passian

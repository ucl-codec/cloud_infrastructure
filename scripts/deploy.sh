#!/bin/bash

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath -s ${0})))

# Start from repo dir
cd "${REPO_DIR}"

cdk deploy --all --profile passian

# To deploy a particular stack, specify the stack name before --profile, like this:
# cdk deploy FbmNodeStack --profile passian

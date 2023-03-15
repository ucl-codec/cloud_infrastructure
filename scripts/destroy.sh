#!/bin/bash

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))

# Start from repo dir
cd "${REPO_DIR}"

cdk destroy --all --profile passian

# To destroy a particular stack, specify the stack name before --profile, like this:
# cdk destroy FbmResearcherServiceStack --profile passian

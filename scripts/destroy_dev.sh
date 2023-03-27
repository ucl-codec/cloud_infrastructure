#!/bin/bash

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))

# Start from repo dir
cd "${REPO_DIR}"

cdk destroy --all --profile passian --context config=dev

# To destroy a particular stack, specify the stack name before --profile, like this:
# cdk destroy passianfl-dev-network-ResearcherServiceStack --profile passian --context config=dev

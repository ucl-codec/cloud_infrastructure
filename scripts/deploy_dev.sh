#!/bin/bash

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))

# Start from repo dir
cd "${REPO_DIR}"

# Deploy system defined in config/dev.cfg
cdk deploy --all --profile passian --context config=dev

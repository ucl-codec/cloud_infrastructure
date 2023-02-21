#!/bin/bash

# Build the Passian docker containers locally.
# This script is for local development/testing and is not part of the AWS deploy.


# Halt script if any command errors
set -e

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath -s ${0})))

docker build -t passian/restful --quiet --file ./docker/restful/Dockerfile ${REPO_DIR}/docker/restful
docker build -t passian/mqtt --quiet --file ./docker/mqtt/Dockerfile ${REPO_DIR}/docker/mqtt
docker build -t passian/gui --quiet --file ./docker/gui/Dockerfile ${REPO_DIR}/docker
docker build -t passian/researcher --quiet --file ./docker/researcher/Dockerfile ${REPO_DIR}/docker
docker build -t passian/node --quiet --file ./docker/node/Dockerfile ${REPO_DIR}/docker

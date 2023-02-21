#!/bin/bash

# Stop and remove any locally running the Passian docker containers.
# This script is for local development/testing and is not part of the AWS deploy.


# Halt script if any command errors
set -e

docker rm -f gui
docker rm -f researcher
docker rm -f node
docker rm -f restful
docker rm -f mqtt

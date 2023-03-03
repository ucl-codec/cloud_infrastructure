#!/bin/bash

# Run Passian docker containers locally.
# This script is for local development/testing and is not part of the AWS deploy.


# Halt script if any command errors
set -e

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))

MQTT_IP="172.18.0.22"
RESTFUL_IP="172.18.0.23"
NODE_IP="172.18.0.24"
GUI_IP="172.18.0.25"
RESEARCHER_IP="172.18.0.26"
RESTFUL_PORT="8000"
NETWORK="fbm_net"

# These variables will be provided to the containers
export MQTT_BROKER="${MQTT_IP}"
export UPLOADS_URL="http://${RESTFUL_IP}:${RESTFUL_PORT}/upload/"

# Persistent storage for local testing and development. Simulates persistent filesystems used on
# cloud deployment, allowing files to persist between runs.
# You can delete this folder to reset the system
NODE_STORAGE="${REPO_DIR}/.local_docker_storage/node"
RESEARCHER_STORAGE="${REPO_DIR}/.local_docker_storage/researcher"

# Create local folders if they don't already exist
mkdir -p "${NODE_STORAGE}/config" "${NODE_STORAGE}/data" "${NODE_STORAGE}/etc" "${NODE_STORAGE}/var" "${NODE_STORAGE}/common"
mkdir -p "${RESEARCHER_STORAGE}/config" "${RESEARCHER_STORAGE}/data" "${RESEARCHER_STORAGE}/etc" "${RESEARCHER_STORAGE}/samples" "${RESEARCHER_STORAGE}/runs" "${RESEARCHER_STORAGE}/var"

# Create the docker network
docker network inspect "${NETWORK}" >/dev/null 2>&1 || \
    docker network create --driver bridge  --subnet=172.18.0.0/16 "${NETWORK}"

# Run MQTT
docker start mqtt 2>/dev/null || docker run -d -p 1883:1883 --net "${NETWORK}" --ip "${MQTT_IP}" --name mqtt passian/mqtt

# Run restful
docker start restful 2>/dev/null || docker run -d -p 8844:8000 --net "${NETWORK}" --ip "${RESTFUL_IP}" --name restful passian/restful

# Run gui
# Note the mounts correspond to the volumes in docker-compose
docker start gui 2>/dev/null || docker run -d -p 8484:8484 --net "${NETWORK}" --ip "${GUI_IP}" \
  -e MQTT_BROKER -e UPLOADS_URL \
  --mount type=bind,source="${NODE_STORAGE}/data",target=/data \
  --mount type=bind,source="${NODE_STORAGE}/etc",target=/fedbiomed/etc \
  --mount type=bind,source="${NODE_STORAGE}/var",target=/fedbiomed/var \
  --mount type=bind,source="${NODE_STORAGE}/common",target=/fedbiomed/envs/common \
  --name gui \
  passian/gui

# Run researcher
# Note the mounts correspond to the volumes in docker-compose
docker start researcher 2>/dev/null || docker run -d -p 8888:8888 -p 6007:6007 --net "${NETWORK}" --ip "${RESEARCHER_IP}" \
  -e MQTT_BROKER -e UPLOADS_URL \
  --mount type=bind,source="${RESEARCHER_STORAGE}/config",target=/config \
  --mount type=bind,source="${RESEARCHER_STORAGE}/data",target=/data \
  --mount type=bind,source="${RESEARCHER_STORAGE}/etc",target=/fedbiomed/etc \
  --mount type=bind,source="${RESEARCHER_STORAGE}/samples",target=/fedbiomed/notebooks/samples \
  --mount type=bind,source="${RESEARCHER_STORAGE}/runs",target=/fedbiomed/runs \
  --mount type=bind,source="${RESEARCHER_STORAGE}/var",target=/fedbiomed/var \
  --name researcher passian/researcher

# Run node
# Note the mounts correspond to the volumes in docker-compose
docker start node 2>/dev/null || docker run -d --net "${NETWORK}" --ip "${NODE_IP}" \
  -e MQTT_BROKER -e UPLOADS_URL \
  --mount type=bind,source="${NODE_STORAGE}/config",target=/config \
  --mount type=bind,source="${NODE_STORAGE}/data",target=/data \
  --mount type=bind,source="${NODE_STORAGE}/etc",target=/fedbiomed/etc \
  --mount type=bind,source="${NODE_STORAGE}/var",target=/fedbiomed/var \
  --mount type=bind,source="${NODE_STORAGE}/common",target=/fedbiomed/envs/common \
  --name node passian/node
# For GPU support add this option (linux only)
#  --gpus all \


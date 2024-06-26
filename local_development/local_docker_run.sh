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
JUPYTER_IP="172.18.0.26"
TENSORBOARD_IP="172.18.0.27"
RESTFUL_PORT="8000"
MQTT_PORT="1883"
NETWORK="fbm_net"
USE_PRODUCTION_GUI="TRUE"
ENABLE_TRAINING_PLAN_APPROVAL="TRUE"
ALLOW_DEFAULT_TRAINING_PLANS="FALSE"
GUI_DEFAULT_ADMIN_EMAIL="admin@passian.local"
GUI_DEFAULT_ADMIN_PW="passian"

# These variables will be provided to the containers
export MQTT_BROKER="${MQTT_IP}"
export MQTT_BROKER_PORT="${MQTT_PORT}"
export UPLOADS_URL="http://${RESTFUL_IP}:${RESTFUL_PORT}/upload/"
export USE_PRODUCTION_GUI="${USE_PRODUCTION_GUI}"
export ENABLE_TRAINING_PLAN_APPROVAL="${ENABLE_TRAINING_PLAN_APPROVAL}"
export ALLOW_DEFAULT_TRAINING_PLANS="${ALLOW_DEFAULT_TRAINING_PLANS}"
export GUI_DEFAULT_ADMIN_EMAIL="${GUI_DEFAULT_ADMIN_EMAIL}"
export GUI_DEFAULT_ADMIN_PW="${GUI_DEFAULT_ADMIN_PW}"

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
docker start mqtt 2>/dev/null || docker run --rm -d -p 1883:1883 --net "${NETWORK}" --ip "${MQTT_IP}" --name mqtt passian/mqtt

# Run restful
docker start restful 2>/dev/null || docker run --rm -d -p 8000:8000 --net "${NETWORK}" --ip "${RESTFUL_IP}" --name restful passian/restful

# Run gui
# Note the mounts correspond to the volumes in docker-compose
docker start gui 2>/dev/null || docker run --rm -d -p 8484:8484 --net "${NETWORK}" --ip "${GUI_IP}" \
  -e MQTT_BROKER -e MQTT_BROKER_PORT -e UPLOADS_URL -e USE_PRODUCTION_GUI -e GUI_DEFAULT_ADMIN_EMAIL -e GUI_DEFAULT_ADMIN_PW \
  --mount type=bind,source="${NODE_STORAGE}/data",target=/data \
  --mount type=bind,source="${NODE_STORAGE}/etc",target=/fedbiomed/etc \
  --mount type=bind,source="${NODE_STORAGE}/var",target=/fedbiomed/var \
  --mount type=bind,source="${NODE_STORAGE}/common",target=/fedbiomed/envs/common \
  --name gui \
  passian/gui

# Run jupyter
# Note the mounts correspond to the volumes in docker-compose
docker start jupyter 2>/dev/null || docker run --rm -d -p 8888:8888 --net "${NETWORK}" --ip "${JUPYTER_IP}" \
  -e MQTT_BROKER -e MQTT_BROKER_PORT -e UPLOADS_URL -e USE_PRODUCTION_GUI \
  --mount type=bind,source="${RESEARCHER_STORAGE}/config",target=/config \
  --mount type=bind,source="${RESEARCHER_STORAGE}/data",target=/data \
  --mount type=bind,source="${RESEARCHER_STORAGE}/etc",target=/fedbiomed/etc \
  --mount type=bind,source="${RESEARCHER_STORAGE}/samples",target=/fedbiomed/notebooks/samples \
  --mount type=bind,source="${RESEARCHER_STORAGE}/runs",target=/fedbiomed/runs \
  --mount type=bind,source="${RESEARCHER_STORAGE}/var",target=/fedbiomed/var \
  --entrypoint /entrypoint_jupyter.bash \
  --name jupyter passian/researcher

# Run tensorboard
# Note the mounts correspond to the volumes in docker-compose
docker start tensorboard 2>/dev/null || docker run --rm -d -p 6007:6007 --net "${NETWORK}" --ip "${TENSORBOARD_IP}" \
  -e MQTT_BROKER -e MQTT_BROKER_PORT -e UPLOADS_URL \
  --mount type=bind,source="${RESEARCHER_STORAGE}/config",target=/config \
  --mount type=bind,source="${RESEARCHER_STORAGE}/data",target=/data \
  --mount type=bind,source="${RESEARCHER_STORAGE}/etc",target=/fedbiomed/etc \
  --mount type=bind,source="${RESEARCHER_STORAGE}/samples",target=/fedbiomed/notebooks/samples \
  --mount type=bind,source="${RESEARCHER_STORAGE}/runs",target=/fedbiomed/runs \
  --mount type=bind,source="${RESEARCHER_STORAGE}/var",target=/fedbiomed/var \
  --entrypoint /entrypoint_tensorboard.bash \
  --name tensorboard passian/researcher

# Run node
# Note the mounts correspond to the volumes in docker-compose
docker start node 2>/dev/null || docker run -d --net "${NETWORK}" --ip "${NODE_IP}" \
  -e MQTT_BROKER -e MQTT_BROKER_PORT -e UPLOADS_URL -e ENABLE_TRAINING_PLAN_APPROVAL -e ALLOW_DEFAULT_TRAINING_PLANS \
  --mount type=bind,source="${NODE_STORAGE}/config",target=/config \
  --mount type=bind,source="${NODE_STORAGE}/data",target=/data \
  --mount type=bind,source="${NODE_STORAGE}/etc",target=/fedbiomed/etc \
  --mount type=bind,source="${NODE_STORAGE}/var",target=/fedbiomed/var \
  --mount type=bind,source="${NODE_STORAGE}/common",target=/fedbiomed/envs/common \
  --name node passian/node \
  --gpus all
# For GPU support add this option (linux only)


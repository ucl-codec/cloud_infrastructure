#!/bin/bash

# UCL PASSIAN - entrypoint script for Fed-BioMed node container
# This script is executed when the container is run

# read config.env
source ~/bashrc_entrypoint

COMMON_DIR="/fedbiomed/envs/common/"
if [ -z "$(ls -1 $COMMON_DIR)" ]; then
  # TODO: test with privilege drop
  # $SETUSER rsync -auxt "/fedbiomed/envs/common_reference/" "$COMMON_DIR"
  rsync -auxt "/fedbiomed/envs/common_reference/" "$COMMON_DIR"
fi


trap finish TERM INT QUIT

# Pass through env variables to conda environment
conda env config vars set MQTT_BROKER="${MQTT_BROKER}" UPLOADS_URL="${UPLOADS_URL}"

source /miniconda/bin/activate fedbiomed-node

/fedbiomed/scripts/fedbiomed_run node start

wait $!

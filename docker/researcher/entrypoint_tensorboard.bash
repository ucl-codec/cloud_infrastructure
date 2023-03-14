#!/bin/bash

# UCL PASSIAN - entrypoint script for Fed-BioMed researcher container
# This script is executed when the container is run

echo "UCL PASSIAN Fed-BioMed Tensorboard container"

# read config.env
#source ~/bashrc_entrypoint

# Pass through env variables to conda environment
conda env config vars set MQTT_BROKER="${MQTT_BROKER}" MQTT_BROKER_PORT="${MQTT_BROKER_PORT}" UPLOADS_URL="${UPLOADS_URL}"

# Initialise and activate conda
source /miniconda/etc/profile.d/conda.sh
conda activate fedbiomed-researcher

trap finish TERM INT QUIT

export PYTHONPATH=/fedbiomed

# Run tensorboard
source /miniconda/etc/profile.d/conda.sh
conda activate fedbiomed-researcher
cd /fedbiomed

echo "Running Tensorboard..."
tensorboard --logdir runs --host 0.0.0.0 --port="${TENSORBOARD_PORT}"
echo "...Tensorboard complete. Container will now exit"

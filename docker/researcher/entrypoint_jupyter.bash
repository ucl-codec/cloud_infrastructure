#!/bin/bash

# UCL PASSIAN - entrypoint script for Fed-BioMed researcher container
# This script is executed when the container is run

# read config.env
#source ~/bashrc_entrypoint

# Pass through env variables to conda environment
conda env config vars set MQTT_BROKER="${MQTT_BROKER}" MQTT_BROKER_PORT="${MQTT_BROKER_PORT}" UPLOADS_URL="${UPLOADS_URL}"

# Initialise and activate conda
source /miniconda/etc/profile.d/conda.sh
conda activate fedbiomed-researcher

trap finish TERM INT QUIT

export PYTHONPATH=/fedbiomed
su -c "export PATH=${PATH} ; cd notebooks ; \
    jupyter notebook --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token='' "

wait $!

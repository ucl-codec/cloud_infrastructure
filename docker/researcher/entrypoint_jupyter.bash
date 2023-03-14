#!/bin/bash

# UCL PASSIAN - entrypoint script for Fed-BioMed researcher container
# This script is executed when the container is run

echo "UCL PASSIAN Fed-BioMed Jupyter container"

# read config.env
#source ~/bashrc_entrypoint

# Pass through env variables to conda environment
conda env config vars set MQTT_BROKER="${MQTT_BROKER}" MQTT_BROKER_PORT="${MQTT_BROKER_PORT}" UPLOADS_URL="${UPLOADS_URL}"

# Initialise and activate conda
source /miniconda/etc/profile.d/conda.sh
conda activate fedbiomed-researcher

trap finish TERM INT QUIT

export PYTHONPATH=/fedbiomed

# Copy default
mkdir -p /fedbiomed/notebooks/defult_notebooks
cd /fedbiomed/notebooks
cp -rf /default_notebooks/. /fedbiomed/notebooks/defult_notebooks/

echo "Running Jupyter..."
jupyter notebook --ip=0.0.0.0 --port="${JUPYTER_PORT}" --no-browser --allow-root --NotebookApp.token=''
echo "...Jupyter complete. Container will now exit"
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
    jupyter notebook --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token='' " &

# Run tensorboard
su -c "source /miniconda/etc/profile.d/conda.sh ; conda activate fedbiomed-researcher ; \
    cd /fedbiomed ; tensorboard --logdir runs" &

#su -c "export PATH=${PATH} ; eval $(conda shell.bash hook) ; \
#    conda activate fedbiomed-researcher ; cd notebooks ; \
#    jupyter notebook --ip=0.0.0.0 --no-browser --allow-root --NotebookApp.token='' " $CONTAINER_USER &

# proxy port for TensorBoard
# enables launching TB without `--host` option (thus listening only on `localhost`)
# + `watch` for easy respawn in case of failure
while true ; do \
    socat TCP-LISTEN:6007,fork,reuseaddr TCP4:127.0.0.1:6006 ; \
    sleep 1 ; \
done &

sleep infinity &

wait $!

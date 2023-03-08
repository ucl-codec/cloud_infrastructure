#!/bin/bash

# UCL PASSIAN - entrypoint script for Fed-BioMed gui container
# This script is executed when the container is run

# Populate server configuration file using runtime environment variables
ini_template="/config_gui.ini.template"
if [ -f "${ini_template}" ]; then
  ini_file="/fedbiomed/gui/config_gui.ini"
  envsubst '${GUI_HOST} ${GUI_PORT} ${GUI_DATA_PATH} ${GUI_DEFAULT_ADMIN_EMAIL} ${GUI_DEFAULT_ADMIN_PW}' < "${ini_template}" > "${ini_file}"
  rm "${ini_template}"
fi

# Wait until the node container has created the ini file
until [ -f "/fedbiomed/etc/config_node.ini" ]
do
   sleep 5
done

# Start the GUI
source /miniconda/etc/profile.d/conda.sh
conda activate fedbiomed-gui

cd /fedbiomed/gui/server
FEDBIOMED_DIR="/fedbiomed" \
  NODE_CONFIG_FILE="config_node.ini" \
  BUILD_DIR="/gui-build" \
  DATA_PATH="/data" \
  HOST="$GUI_HOST" \
  PORT="$GUI_PORT" \
  DEBUG="False" \
  FLASK_ENV="production" \
  gunicorn -b 0.0.0.0:${GUI_PORT} -w 4 --preload --timeout 20 --error-logfile '-' --log-level 'debug' 'app:app'

#!/bin/bash

# UCL PASSIAN - entrypoint script for Fed-BioMed gui container
# This script is executed when the container is run

echo "UCL PASSIAN Fed-BioMed gui container"

# Pass through env variables to conda environment
conda env config vars set USE_PRODUCTION_GUI="${USE_PRODUCTION_GUI}"

# Populate server configuration file using runtime environment variables
ini_template="/config_gui.ini.template"
if [ -f "${ini_template}" ]; then
  ini_file="/fedbiomed/gui/config_gui.ini"
  envsubst '${GUI_HOST} ${GUI_PORT} ${GUI_DATA_PATH} ${GUI_DEFAULT_ADMIN_EMAIL} ${GUI_DEFAULT_ADMIN_PW}' < "${ini_template}" > "${ini_file}"
  rm "${ini_template}"
fi

# Wait until the node container has created the ini file
echo "Waiting for node config file..."
until [ -f "/fedbiomed/etc/config_node.ini" ]
do
   sleep 5
done
echo "...done"

# Start the GUI
source /miniconda/etc/profile.d/conda.sh
conda activate fedbiomed-gui

cd /fedbiomed/gui/server

# Replace pre-built gui files with default files from Docker build
if [ -d "/fedbiomed/var/gui-build" ];then
  rm -Rf "/fedbiomed/var/gui-build";
fi
mkdir -p /fedbiomed/var/gui-build
cp -rf /gui-build/. /fedbiomed/var/gui-build/

if [ "${USE_PRODUCTION_GUI}" = "TRUE" ]; then
  echo "Running production gui..."
  FEDBIOMED_DIR="/fedbiomed" \
    NODE_CONFIG_FILE="config_node.ini" \
    BUILD_DIR="/gui-build" \
    DATA_PATH="/data" \
    HOST="$GUI_HOST" \
    PORT="$GUI_PORT" \
    DEBUG="False" \
    FLASK_ENV="production" \
    gunicorn -b 0.0.0.0:${GUI_PORT} --worker-class=gevent -w 4 --preload --timeout ${GUI_TIMEOUT} --error-logfile '-' --log-level 'debug' 'app:app'
else
  echo "Running development gui..."
  /fedbiomed/scripts/fedbiomed_run gui host 0.0.0.0 data-folder /data config config_node.ini start
fi

#!/bin/bash

# Create a password and store as AWS SecretString parameter
#
# Usage: initialise_gui_default_pw.sh aws-param-name aws-profile-name
#


# Exit if any command fails
set -e

# Get the directory containing scripts
SCRIPTS_DIR=$(dirname $(realpath ${0}))

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))

param_default_gui_pw="${1}"
profile_name="${2:-passian}"

if [ -z "${param_default_gui_pw}" ]
then
    echo "Parameter name ${param_default_gui_pw} appears to be empty"
    exit 1
fi
if [ -z "${profile_name}" ]
then
    echo "AWS profile name ${profile_name} appears to be empty"
    exit 1
fi

# Check that credentials are working. Otherwise the parameter lookup will always report not found
${SCRIPTS_DIR}/check_credentials.sh "${profile_name}"

if ! aws ssm get-parameter --name "${param_default_gui_pw}" --profile "${profile_name}" > /dev/null 2>&1; then
    echo "Creating default FBM gui password and storing in AWS secret ${param_default_gui_pw}"
    local default_pw
    default_pw=$(aws secretsmanager get-random-password --profile "${profile_name}" --output text)
    aws ssm put-parameter --name "${param_default_gui_pw}" --value "${default_pw}" --type "SecretString" --profile "${profile_name}"
fi

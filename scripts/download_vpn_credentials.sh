#!/bin/bash

# Download a user's VPN client configuration file from PassianFL AWS parameter store
#
# Usage:
#   download_vpn_credentials.sh <config> <node> <client> <profile>
# where:
#   <config> is the name of the config environment (e.g. dev)
#   <node> is the name of the node, matching the node section in the config file (e.g. nodea)
#   <client> is the name of the client machine/user to generate the certificate for (e.g. foo)
#   <profile> is the name of your local aws profile holding your aws credentials (e.g. passian)


# Exit if any command fails
set -e

# Get the directory containing scripts
SCRIPTS_DIR=$(dirname $(realpath ${0}))

config_name="${1}"
node_name="${2}"
client_name="${3}"
profile_name="${4:-passian}"

ca_name="${config_name}-${node_name}"
credentials_param_name="${ca_name}-${client_name}-vpn-profile"

if [ -z "${config_name}" ]
then
    echo "Config file name must be specified as first argument"
    exit 1
fi
if [ -z "${node_name}" ]
then
    echo "Node name must be specified as second argument"
    exit 1
fi
if [ -z "${client_name}" ]
then
    echo "Client name must be specified as third argument"
    exit 1
fi
if [ -z "${profile_name}" ]
then
    echo "AWS profile name ${profile_name} must be specified as fourth argument"
    exit 1
fi

# Check that credentials are working. Otherwise the bucket lookup will always report not found
${SCRIPTS_DIR}/check_credentials.sh "${profile_name}"

root=$(realpath ~/passian_vpn_certificates)
profile_dir="${root}/vpn_configuration_files"
mkdir -p "${profile_dir}"

config_name="${profile_dir}/${credentials_param_name}.ovpn"

# Check if this profile has already been downloaded
if [ -f "${config_name}" ]; then
    echo "This VPN client configuration file has already been downloaded to ${config_name}"
    exit 1
fi

aws ssm get-parameter --name "${credentials_param_name}" --profile "${profile_name}" > "${config_name}"
echo "This VPN client configuration file has been downloaded to ${config_name}"
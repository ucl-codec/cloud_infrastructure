#!/bin/bash

# Exit if any command fails
set -e

# Get the directory containing scripts
SCRIPTS_DIR=$(dirname $(realpath ${0}))

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))


get_config_value() {
    local config_file="${1}"
    local section_name="${2}"
    local param_name="${3}"

    if [ -z "${config_file}" ]
    then
        echo "Config file name ${config_file} appears to be empty"
        exit 1
    fi
    if [ -z "${section_name}" ]
    then
        echo "Section name ${section_name} appears to be empty"
        exit 1
    fi
    if [ -z "${param_name}" ]
    then
        echo "Param name ${param_name} appears to be empty"
        exit 1
    fi

    # Note we declare value local _before_ assigning it; this allows the exit code from $() to pass
    # through, triggering set -e where necessary
    local value
    value=$(crudini --get "${config_file}" "${section_name}" "${param_name}")

    #...but just to be sure, we check that tge value is not empty
    if [ -z "${value}" ]
    then
        echo "Config file ${config_file} does not contain value ${section_name}->${param_name}, or it is empty"
        exit 1
    fi

    # Return value
    echo "${value}"
}


process_config_file() {
    local config_name="${1}"
    local profile_name="${2}"
    local config_file="${REPO_DIR}/config/${config_name}.cfg"
    if [ ! -f "${config_file}" ]; then
        echo "Config file ${config_file} does not exist"
        exit 1
    fi
    echo "Using configuration from ${config_file}"

    sections=$(crudini --get --list "${config_file}")

    for section_name in ${sections}; do
        echo "Processing config file section: ${section_name}"

        local param_vpn_cert_arn
        param_vpn_cert_arn=$(get_config_value "${config_file}" "${section_name}" "param_vpn_cert_arn")
        "${SCRIPTS_DIR}/initialise_vpn_certs.sh" "${param_vpn_cert_arn}" "${profile_name}"

        if [ "${section_name}" != "network" ]; then
            local bucket_name
            bucket_name=$(get_config_value "${config_file}" "${section_name}" "bucket_name")
            "${SCRIPTS_DIR}/initialise_bucket.sh" "${bucket_name}" "${profile_name}"

            # Warning: do not inline local with pw_param_name, otherwise exit code will be swallowed
            local pw_param_name
            pw_param_name=$(get_config_value "${config_file}" "${section_name}" "param_default_gui_pw")
            "${SCRIPTS_DIR}/initialise_gui_default_pw.sh" "${pw_param_name}" "${profile_name}"
        fi
    done

}


config_name="${1}"
profile_name="${2:-passian}"

# Check that credentials are working. Otherwise the bucket lookup will always report not found
${SCRIPTS_DIR}/check_credentials.sh "${profile_name}"

# Create any required S3 buckets that do not currently exist
process_config_file "${config_name}" "${profile_name}"

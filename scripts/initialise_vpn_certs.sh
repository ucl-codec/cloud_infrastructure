#!/bin/bash

# Create VPN certificates and store in AWS

# Exit if any command fails
set -e

generate_and_upload_cert() {
    ca_name="${1}"
    server_domain="${2}"
    param_vpn_cert_arn="${3}"
    profile_name="${4}"

    root=$(realpath ~/passian_vpn_certificates)
    mkdir -p "${root}/passian_cas"

    verbose="--silent --silent-ssl"

    # Git checkout
    git_repo="https://github.com/OpenVPN/easy-rsa.git"
    git_checkout="${root}/easy-rsa"
    easyrsa="${git_checkout}/easyrsa3/easyrsa"
    if [ ! -d "${git_checkout}" ]; then
        echo " - Cloning ${git_repo} to ${git_checkout}"
        git clone "${git_repo}" "${git_checkout}" --quiet
    fi

    ca_root="${root}/passian_cas/${ca_name}"
    ca_crt="${ca_root}/ca.crt"
    server_crt="${ca_root}/issued/${server_domain}.crt"
    server_key="${ca_root}/private/${server_domain}.key"

    # Initialise the PKI environment
    if [ ! -d "${ca_root}" ]; then
        echo " - Initialising PKI environment for ${server_domain}"
        "${easyrsa}" --pki-dir="${ca_root}" $verbose init-pki
    fi

    # Create the CA
    if [ ! -f "${ca_crt}" ]; then
        echo " - Creating CA for ${server_domain}"
        "${easyrsa}" --pki-dir="${ca_root}" --req-cn="${server_domain}" --batch $verbose build-ca nopass
    fi

    # Create the server certificate
    if [ ! -f "${server_crt}" ]; then
        echo " - Creating server certificate for ${server_domain}"
        "${easyrsa}" --pki-dir="${ca_root}" --batch $verbose build-server-full "${server_domain}" nopass
    fi

    # Store server certificate in AWS
    echo " - Uploading certificate ${server_domain} to AWS"
    cert_arn=$(aws acm import-certificate --certificate "fileb://${server_crt}" --private-key "fileb://${server_key}" --certificate-chain "fileb://${ca_crt}" --output text --profile ${profile_name})

    # Store certificate ARN in parameter
    echo " - Storing the certificate ARN in AWS System Parameter ${param_vpn_cert_arn}"
    aws ssm put-parameter --name "${param_vpn_cert_arn}" --description "ARN of VPN server certificate for server ${server_domain} in VPN ${ca_name}" --value "${cert_arn}" --type "String" --profile "${profile_name}" >> /dev/null
}


# Get the directory containing scripts
SCRIPTS_DIR=$(dirname $(realpath ${0}))

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))

config_name="${1}"
node_name="${2}"
profile_name="${3:-passian}"
server_name="server"

ca_name="${config_name}-${node_name}"
param_vpn_cert_arn="passianfl-${ca_name}-vpn-server-cert-arn"
server_domain="${server_name}.${node_name}.${config_name}"

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
if [ -z "${profile_name}" ]
then
    echo "AWS profile name ${profile_name} must be specified as third argument"
    exit 1
fi

# Check that credentials are working. Otherwise the bucket lookup will always report not found
${SCRIPTS_DIR}/check_credentials.sh "${profile_name}"

if aws ssm get-parameter --name "${param_vpn_cert_arn}" --profile "${profile_name}" >> /dev/null 2>&1; then
    echo " - Skipping VPN certificate creation as parameter ${param_vpn_cert_arn} already exists"
else
    echo " - Creating VPN certificate, uploading and storing arn in parameter ${param_vpn_cert_arn}"
    generate_and_upload_cert "${ca_name}" "${server_domain}" "${param_vpn_cert_arn}" "${profile_name}"
fi

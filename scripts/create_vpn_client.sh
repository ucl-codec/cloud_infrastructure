#!/bin/bash

# Create VPN client certificates and store in AWS
#
# Usage:
#   create_vpn_client.sh <config> <node> <client> <profile>
# where:
#   <config> is the name of the config file (e.g. dev)
#   <node> is the name of the node, matching the node section in the config file (e.g. nodea)
#   <client> is the name of the client machine/user to generate the certificate for (e.g. foo)
#   <profile> is the name of your local aws profile holding your aws credentials (e.g. passian)


# Exit if any command fails
set -e

generate_and_upload_client_cert() {
    ca_name="${1}"
    client_domain="${2}"
    credentials_param_name="${3}"
    vpn_endpoint_id_param_name="${4}"
    profile_name="${5}"

    verbose="--silent --silent-ssl"

    mkdir -p ~/passian_vpn_certificates
    root=$(realpath ~/passian_vpn_certificates)
    git_checkout="${root}/easy-rsa"
    easyrsa="${git_checkout}/easyrsa3/easyrsa"

    ca_root="${root}/passian_cas/${ca_name}"
    ca_crt="${ca_root}/ca.crt"
    client_crt="${ca_root}/issued/${client_domain}.crt"
    client_key="${ca_root}/private/${client_domain}.key"


    # Verify that the CA exists
    if [ ! -f "${ca_crt}" ]; then
        echo "Certificate authority files not found on this machine at ${ca_root}"
        exit 1
    fi

    # Fetch the VPN ID from the parameter which should be populated during CDK deployment
    vpn_endpoint_id=$(aws ssm get-parameter --name "${vpn_endpoint_id_param_name}" --query Parameter.Value --output text --profile "${profile_name}")

    # The command should fail before getting here if using set -e but this is an additional check
    if [ $? -ne 0 ]; then
        echo "Failed to fetch VPN endpoint ID from parameter ${vpn_endpoint_id_param_name}"
        exit 1
    fi

    # Create the client certificate if it does not already exist
    if [ -f "${client_crt}" ]; then
        echo " - Skipping creation of client certificate as it already exists at ${client_crt}"
    else
        echo " - Creating client certificate for ${client_domain}"
        "${easyrsa}" --pki-dir="${ca_root}" --batch $verbose build-client-full "${client_domain}" nopass

        # Store client certificate in AWS
        echo " - Uploading client certificate ${client_domain} to AWS"
        cert_arn=$(aws acm import-certificate --certificate "fileb://${client_crt}" --private-key "fileb://${client_key}" --certificate-chain "fileb://${ca_crt}" --output text --profile ${profile_name})
        echo " - Certificate has been stored in ${cert_arn}"
    fi

    mkdir -p "${ca_root}/vpn_profiles"
    vpn_profile="${ca_root}/vpn_profiles/${client_domain}.ovpn"

    ovpn_template=$(aws ec2 export-client-vpn-client-configuration --client-vpn-endpoint-id ${vpn_endpoint_id} --output text --profile passian)
    client_cert_txt=$(<${client_crt})
    client_key_txt=$(<${client_key})

    beg_match="-----BEGIN CERTIFICATE-----"
    certs=$'\n'"<cert>"$'\n'"${beg_match}${client_cert_txt#*${beg_match}}"$'\n'"</cert>"$'\n'"<key>"$'\n'"${client_key_txt}"$'\n'"</key>"
    ca_match="</ca>"
    user_ovpn_file="dhcp-option DOMAIN-ROUTE ."$'\n'"${ovpn_template%%${ca_match}*}${ca_match}${certs}${ovpn_template##*${ca_match}}"
    echo " - Writing ovpn file ${vpn_profile}"
    echo "${user_ovpn_file}" > "${vpn_profile}"

    # Upload new client configuration file to Parameter Store as a SecureString
    echo " - Uploading ovpn file to SecureString parameter ${credentials_param_name}"
    aws ssm put-parameter --name "${credentials_param_name}" --description "VPN client configuration file for ${client_domain} in VPN ${ca_name}" --value "${user_ovpn_file}" --type "SecureString" --tier Advanced --profile "${profile_name}" >> /dev/null

}

# Get the directory containing scripts
SCRIPTS_DIR=$(dirname $(realpath ${0}))

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))

config_name="${1}"
node_name="${2}"
client_name="${3}"
profile_name="${4:-passian}"

ca_name="${config_name}-${node_name}"
credentials_param_name="passianfl-${ca_name}-${client_name}-vpn-profile"
vpn_endpoint_id_param_name="passianfl-${ca_name}-vpn-endpoint-id"
client_domain="${client_name}.${node_name}.${config_name}"

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

if aws ssm get-parameter --name "${credentials_param_name}" --profile "${profile_name}" >> /dev/null 2>&1; then
    echo " - Skipping VPN client certificate creation as parameter ${credentials_param_name} already exists"
else
    echo " - Creating VPN client certificate, uploading and storing in SecureString parameter ${credentials_param_name}"
    generate_and_upload_client_cert "${ca_name}" "${client_domain}" "${credentials_param_name}" "${vpn_endpoint_id_param_name}" "${profile_name}"
fi



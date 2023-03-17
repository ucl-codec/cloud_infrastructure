#!/bin/bash

# Return error code and display error if cannot connect with AWS credentials

profile_name="${1:-passian}"

if [ -z "${profile_name}" ]
then
    echo "AWS profile name has not been specified"
    exit 1
fi

if ! aws sts get-caller-identity --profile "${profile_name}" >> /dev/null 2>&1; then
    echo "Failed to connect using AWS credentials profile ${profile_name}"
    exit 1
fi

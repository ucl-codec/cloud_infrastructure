#!/bin/bash

# Create an S3 bucket if it does not already exist
#
# Usage: initialise_bucket.sh bucket-name aws-profile-name
#


# Exit if any command fails
set -e

# Get the directory containing scripts
SCRIPTS_DIR=$(dirname $(realpath ${0}))

# Get the repo root directory
REPO_DIR=$(dirname $(dirname $(realpath ${0})))


bucket_name="${1}"
profile_name="${2:-passian}"

if [ -z "${bucket_name}" ]
then
    echo "Bucket name ${bucket_name} appears to be empty"
    exit 1
fi
if [ -z "${profile_name}" ]
then
    echo "AWS profile name ${profile_name} appears to be empty"
    exit 1
fi

# Check that credentials are working. Otherwise the bucket lookup will always report not found
${SCRIPTS_DIR}/check_credentials.sh "${profile_name}"

# Check if bucket already exists. Note: will fail if user does not have access to bucket
if ! aws s3api head-bucket --bucket "${bucket_name}" --profile "${profile_name}" 2>/dev/null; then
    echo "Creating bucket ${bucket_name}"
    aws s3api create-bucket --bucket "${bucket_name}" --create-bucket-configuration LocationConstraint=eu-west-2 --object-ownership BucketOwnerEnforced --profile "${profile_name}"

    echo "Adding public access block for bucket ${bucket_name}"
    aws s3api put-public-access-block --bucket "${bucket_name}" --public-access-block-configuration "BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true" --profile "${profile_name}"
fi

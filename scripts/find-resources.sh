#!/bin/bash

if [ -z "${1}" ]; then
  echo "Display a list of AWS resources used by the VPC (specified by AWS VPC ID)"
  echo "Usage: find-resources VPCID"
  echo "where VPCID is the VPC ID of the VPC"
  exit 1
fi

vpc=${1}
aws ec2 describe-internet-gateways --filters 'Name=attachment.vpc-id,Values='$vpc --profile passian | grep InternetGatewayId
aws ec2 describe-subnets --filters 'Name=vpc-id,Values='$vpc --profile passian | grep SubnetId
aws ec2 describe-route-tables --filters 'Name=vpc-id,Values='$vpc --profile passian | grep RouteTableId
aws ec2 describe-network-acls --filters 'Name=vpc-id,Values='$vpc --profile passian | grep NetworkAclId
aws ec2 describe-vpc-peering-connections --filters 'Name=requester-vpc-info.vpc-id,Values='$vpc --profile passian | grep VpcPeeringConnectionId
aws ec2 describe-vpc-endpoints --filters 'Name=vpc-id,Values='$vpc --profile passian | grep VpcEndpointId
aws ec2 describe-nat-gateways --filter 'Name=vpc-id,Values='$vpc --profile passian | grep NatGatewayId
aws ec2 describe-security-groups --filters 'Name=vpc-id,Values='$vpc --profile passian | grep GroupId
aws ec2 describe-instances --filters 'Name=vpc-id,Values='$vpc --profile passian | grep InstanceId
aws ec2 describe-vpn-connections --filters 'Name=vpc-id,Values='$vpc --profile passian | grep VpnConnectionId
aws ec2 describe-vpn-gateways --filters 'Name=attachment.vpc-id,Values='$vpc --profile passian | grep VpnGatewayId
aws ec2 describe-network-interfaces --filters 'Name=vpc-id,Values='$vpc --profile passian | grep NetworkInterfaceId

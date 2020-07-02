#!/bin/bash
#
# Script: runssh.sh
#
# Description: Quick-n-dirty bash wrapper for ssh into AWS instance
#
# Author: Bill Fanselow 2020-06-05
#
#--------------------------------------------------------------------------------------------------
user='ec2-user'
region='us-east-2'
keypath='__path_to_pem_file__'

state=`aws ec2 describe-instances --query "Reservations[*].Instances[*].State.Name" --output=text`
if [ "X${state}" = "Xstopped" ]; then
  echo ""
  echo "WARNING - Instance is in state=stopped"
  echo ""
  exit 1
fi

pubip=`aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicIpAddress" --output=text`

if [ "X${pubip}" = "X" ]; then
  echo ""
  echo "ERROR - Public-IP not retrieved"
  echo ""
  exit 1
fi

ipstr="${pubip//./-}"
host="ec2-${ipstr}.${region}.compute.amazonaws.com"
echo "HOST: $host"

cmd="ssh -i $keypath ${user}@${pubip}"
echo $cmd
$cmd

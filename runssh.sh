#!/bin/bash
#
# Script: runssh.sh
#
# Description: Wrapper for ssh into AWS instance
#
# Author: Bill Fanselow 2020-06-05
#
#--------------------------------------------------------------------------------------------------


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

user='ec2-user'

region='us-east-2'
keypath='/home/wfanselow/.ssh/aws_admin.id_rsa.pem'

ipstr="${pubip//./-}"
host="ec2-${ipstr}.${region}.compute.amazonaws.com"
echo "HOST: $host"

cmd="ssh -i $keypath ${user}@${pubip}"
echo $cmd
$cmd

#!/bin/bash
#
# Script: pushfile.sh
#
# Description: Quick-n-dirty simple bash wrapper around aws cli for scp a file to AWS instance
#
# Author: Bill Fanselow 2020-06-05
#
#-----------------------------------------------------------------

user='ec2-user'
keypath='__path_to_pem_file__'

file=$1

if [ "X${file}" = "X" ]; then
  echo "ERROR - No file requested"
  exit 1
fi

remote_path='.'
if [ "X$2" != "X" ]; then
  remote_path=$2
fi

pubip=`aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicIpAddress" --output=text`

dest_path="/home/${user}/${remote_path}"

cmd="scp -i $keypath $file ${user}@${pubip}:${dest_path}"
echo $cmd
$cmd

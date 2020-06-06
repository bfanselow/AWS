#!/bin/sh
##
## File: ec2meta.sh
##
## Description:
##  Using Instance-Metadata-Service (IMDS) to get a meta-data attribute of a local
##  EC2 isntance. By default, will retrieve the "public-ipv4" of instance
##
## Usage:
##  Run this from the EC2 instance to get metadat including public-ipv4
##  [ec2-user]$ ./mdata.sh [<data-key>]
##
##  If <data-key> == 'help', then all available meta-data keys are returned.
##
## IMDS Notes:
## IMDS provides access to temporary, frequently rotated instance data, removing the headache of
## hardcoding or distributing ephemeral (sensitive) data. Attached locally to every EC2 instance,
## the "IMDS" runs on a special "link local" IP address of 169.254.169.254. Therefore, only software
## running on the instance can access it. For applications with access to IMDS, it makes available
## metadata about the instance.
##
## This script curently uses IMDSv1 to get the data. Instances can be configured to use the
## (more secure) IMDSv2 ersion with short-lived token. If this is configured, change the commands below
## to use the following sequence:
##
##   TOKEN=`curl -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600"`
##   curl -H "X-aws-ec2-meta
##
############################################################################################

curl='/usr/bin/curl'

## Make these vars in case they change
imds_ip='169.254.169.254'
imds_uri="http://${imds_ip}/latest/meta-data/"

## default key to retrieve
data_key='public-ipv4'

## override default?
if [ "X${1}" != "X" ]; then
  data_key=$1
fi

## get the data
if [ $data_key == "help" ]; then
  $curl -s $imds_uri
else
  VALUE=`$curl -s ${imds_uri}${data_key}`
  echo "KEY: $data_key"
  echo "$VALUE"
fi

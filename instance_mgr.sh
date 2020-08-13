#!/bin/bash
#
# Script: instance_status.sh
#
# Description: Use aws-cli to start, stop, or check-status of an AWS EC2 instance
#
# Author: Bill Fanselow 2020-06-05
#
# Step required for installing and configureing aws cli:
#
# 1) Setup vitualenv
# $ virtualenv -p python3.6 venv
# $ . venv/bin/activate
# $ pip install awscli
#
# 2) Create an IAM user on AWS UI
# 3) Create User key for this user; copy/download key info
# 4) Verify the name of your "region"
#
# 5) Configure aws cli for the user using key info and region:
# $ aws configure
#  AWS Access Key ID [None]: ****************
#  AWS Secret Access Key [None]: **************
#  Default region name [None]: us-east-2
#  Default output format [None]: json
#
#
# NOTICE: Authentication tokens are time stamped. If your local computor's datetime is off (by a few minutes or more)
# relative to AWS servers your credentials will be invalid and you will get the following error:
#  "AWS was not able to validate the provided credentials"
# Solution: Set your time with NOT or the following command:
#   $ sudo date -s "$(wget -qSO- --max-redirect=0 google.com 2>&1 | grep Date: | cut -d' ' -f5-8)Z"
#
#--------------------------------------------------------------------------------------------------

MYNAME=instance_status.sh
VERBOSE=0
DEBUG=0

## Defauult instance-ID
ID='i-08b039378c97e5f96'

##-----------------------------------------------------------------------------
## Print all usage details
usage()
{
    exit_code=$1

    echo "Usage:"
    echo ""
    echo "./$MYNAME"
    echo "  -h --help"
    echo "  --iid=<instance-id>"
    echo "  <start|stop|status>"
    echo "  -v --verbose"
    echo ""

    if [ "X${exit_code}" != "X" ]; then
      exit $exit_code
    fi
}
##-----------------------------------------------------------------------------
## Retrieve public-IP address
get_pub_ip()
{
  instance_id=$1
  pubip=`aws ec2 describe-instances --query "Reservations[*].Instances[*].PublicIpAddress" --output=text`
  if [ "X${pubip}" = "X" ]; then
    echo ""
    echo "ERROR - Public-IP not retrieved"
    echo ""
    exit 1
  fi
  echo $pubip

}
##-----------------------------------------------------------------------------
## main()
##-----------------------------------------------------------------------------
if [ "$1" = "" ]; then
   echo ""
   echo "$MYNAME: Cmd-line ERROR: must specify an input action (start|stop|status)"
   usage 1
fi

## Parse the args: options specified by --<option> (or -o); key/value pairs specified by "<key>=<val>"
while [ "$1" != "" ]; do
    PARAM=`echo $1 | awk -F= '{print $1}'`
    VALUE=`echo $1 | awk -F= '{print $2}'`
    case $PARAM in
        -h | --help)
            usage 0
            exit
            ;;
        -v | --verbose)
            VERBOSE=1
            ;;
        start)
            ACTION='start'
            ;;
        stop)
            ACTION='stop'
            ;;
        status)
            ACTION='status'
            ;;
        -i | --iid)
            ID=$VALUE
            ;;
        *)
            echo "$MYNAME: Cmd-line ERROR: unknown parameter \"$PARAM\""
            usage 0
            exit 1
            ;;
    esac
    shift
done

state=`aws ec2 describe-instances --query "Reservations[*].Instances[*].State.Name" --output=text`

if [ "X${ACTION}" = "Xstart" ]; then

  ## are we already in stopped state?
  if [ "X${state}" != "Xstopped" ]; then
    echo ""
    echo "WARNING - Instance is currently in state=${state}"
    echo ""
    exit 1
  fi

  ## start
  echo "Starting instance: $ID"
  aws ec2 start-instances --instance-ids $ID


elif [ "X${ACTION}" = "Xstop" ]; then
  ## are we already in stopped state?
  if [ "X${state}" == "Xstopped" ]; then
    echo ""
    echo "WARNING - Instance is already in state=stopped"
    echo ""
    exit 1
  fi

  ## stop
  echo "Stopping instance: $ID"
  aws ec2 stop-instances --instance-ids $ID

else
  echo ""
  if [ $VERBOSE -ne 0 ]; then
    ##aws ec2 describe-instances
    aws ec2 start-instances --instance-ids $ID
  else
    echo "Instance (${ID}) STATE: $state"
    if [ "X${state}" != "Xstopped" ]; then
      pubip=$(get_pub_ip ${ID})
      echo "PUBLIC-IP: $pubip"
    fi
  fi
fi

exit 0

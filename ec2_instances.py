#!/usr/bin/env python3
"""

  Module: ec2_instances.py
  Description:
    Retrieve information about EC2 instances.

  Author: Bill Fanselow 2020-07-01

"""
import os
import sys
import argparse
import boto3

myname = os.path.basename(__file__)

DEBUG = 0
VERBOSITY = 0

all_states = {
  'pending': 0,
  'running': 16,
  'shutting-down': 32,
  'terminated': 48,
  'stopping': 64,
  'stopped': 80
}
#######################################
# IMPORTANT-INFO: Stopped vs Terminated
# In both "stopped" and "terminated" states the instance is shutdown and the virtual machine that was
# provisioned is permanently removed and no instance charges will be incurred. However, when "stopped",
# the attached bootable EBS volume will not be deleted (as it will be for "terminated").
# The data on your EBS volume will remain after stopping while all information on the local (ephemeral)
# hard drive will be lost as usual. The volume will continue to persist in its availability zone.
# Standard charges for EBS volumes will apply even when stopped.
# The ability to stop an instance is only supported on instances that were launched using an EBS-based
# AMI where the root device data is stored on an attached EBS volume as an EBS boot partition instead
# of being stored on the local instance itself. As a result, one of the key advantages of starting a
# stopped instance is that it should theoretically have a faster boot time. When you start a stopped
# instance the EBS volume is simply attached to the newly provisioned instance. Although, the AWS-id
# of the new virtual machine will be the same, it will have new IP Addresses, DNS Names, etc.
# You shouldn't think of starting a stopped instance as simply restarting the same virtual machine
# that you just stopped as it will most likely be a completely different virtual machine that will
# be provisioned to you.
# You should only stop an instance if you plan to start it again within a reasonable timeframe.
# Otherwise, you might want to backup all the data and terminate an instance instead of stopping
# it for cost saving purposes.
#######################################

## Add whatver attributes we are interested in
attributes = ['name', 'type', 'state', 'private_ip', 'public_ip', 'launch_time']

#-------------------------------------------------------------------------------------------
def get_instance_data(ec2, state):

    filters = []
    if state:
        state_filter = { 'Name':'instance-state-name', 'Values': [state]}
        filters = [state_filter]

    all_instances = ec2.instances.filter(Filters=filters)

    instance_data = {}
    for instance in all_instances:
        for tag in instance.tags:
            if 'Name'in tag['Key']:
                name = tag['Value']

        instance_data[instance.id] = {
            'name': name,
            'type': instance.instance_type,
            'state': instance.state['Name'],
            'private_ip': instance.private_ip_address,
            'public_ip': instance.public_ip_address,
            'launch_time': instance.launch_time
            }
    return instance_data

#-------------------------------------------------------------------------------------------
def parse_input_args():
    # Create the parser with a description of what the script does, optional prog-name, and optional usage
    parser = argparse.ArgumentParser( prog=myname,
                                      usage='%(prog)s [options] <path>',
                                      description='Retrieve information on EC2 instances'
                                     )

    parser.add_argument('-d','--debug', required=False, metavar='debug', type=int, choices=[0,1,2], help='set debug level')
    parser.add_argument('-v', required=False, action='count', help='set verbosity level')
    parser.add_argument('--state', '-s', action="store", dest="state")

    args = parser.parse_args()

    return args

#-------------------------------------------------------------------------------------------
if __name__ == '__main__':

    state = None
    input_args = parse_input_args()

    if input_args.debug:
        DEBUG = input_args.debug

    if DEBUG > 1:
        print("%s: INPUT-ARGS: %s" % (myname, vars(input_args)))

    if input_args.v:
        VERBOSITY = input_args.v

    if input_args.state:
        state = input_args.state
        if state not in all_states:
            print("%s: State [%s] is not a valid state" % (myname, state))
            sys.exit(1)

    ec2 = boto3.resource('ec2')
    d_instance_data = get_instance_data(ec2, state)
    print("-"*50)
    if state:
        print("STATE=%s" % state)
    N = len(d_instance_data.keys())
    print("INSTANCE-COUNT: %d" % N)

    for instance_id, instance in d_instance_data.items():
        print("ID: {0}".format(instance_id))
        for key in attributes:
            print("  {0}: {1}".format(key, instance[key]))

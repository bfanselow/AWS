#!/usr/bin/env python
"""

  Script: instance_status.py
  Description: Start, stop, or check-status of an AWS EC2 instance
  Author: Bill Fanselow 2020-06-05

"""

import os
import sys
import boto3
import argparse

myname = os.path.basename(__file__)

DEBUG = 0
VERBOSITY = 0

#-----------------------------------------------------------------------------
def get_instance_data( ec2, instance_id=None ):
    """ Retrieve all instances. Compile a dict of instance data
    Args:
     * (obj): ec2.resource
     * (list): OPTIONAL instance-id to return
    Returns: (dict) instance data
    """

    instances = ec2.instances.all()

    instance_data = {}
    for instance in instances:
        for tag in instance.tags:
            if 'Name'in tag['Key']:
                name = tag['Value']
        id = instance.id
        if instance_id:
            if id != instance_id:
                continue
        instance_data[instance.id] = {
            'name': name,
            'type': instance.instance_type,
            'state': instance.state['Name'],
            'private_ip': instance.private_ip_address,
            'public_ip': instance.public_ip_address,
            'launch_time': instance.launch_time
        }
    return instance_data

#-----------------------------------------------------------------------------
def stop_instance( ec2_client, instance_id ):
    """ Stop the passed instance """
    print("%s: STOPPING instance (%s)" % (myname, instance_id))
    ec2.instances.filter(InstanceIds=[instance_id]).stop()

#-----------------------------------------------------------------------------
def start_instance( ec2_client, instance_id ):
    """ Start the passed instance """
    print("%s: STARTING instance (%s)" % (myname, instance_id))
    ec2.instances.filter(InstanceIds=[instance_id]).start()

#-----------------------------------------------------------------------------
def parse_input_args():
    """ Create an arg-parser, parse and return input args"""
    parser = argparse.ArgumentParser( prog=myname,
                                      usage='%(prog)s [options] <path>',
                                      description='Start/Stop/Status for an EC2 Instance'
                                     )

    parser.add_argument('-i','--instance', required=False, metavar='instance', help='specify instance-id')
    parser.add_argument('-d','--debug', required=False, metavar='debug', type=int, choices=[0,1,2], help='set debug level')
    parser.add_argument('-v', required=False, action='count', help='set verbosity level')
    parser.add_argument('--start', action='store_true', help='start an instance')
    parser.add_argument('--stop', action='store_true', help='stop an instance')
    parser.add_argument('--status', action='store_true', help='get instance status')

    args = parser.parse_args()

    return args

#-----------------------------------------------------------------------------
# main()
if __name__ == '__main__':

    input_args = parse_input_args()

    if input_args.debug:
        DEBUG = input_args.debug
    if DEBUG > 1:
        print("%s: INPUT-ARGS: %s" % (myname, vars(input_args)))
    if input_args.v:
        VERBOSITY = input_args.v

    instance_id = None
    if input_args.instance:
        instance_id = input_args.instance

    ec2 = boto3.resource('ec2')

    instance_data = get_instance_data(ec2, instance_id)

    if not len(instance_data.keys()):
        print("No instances matching input ID (%s)" % (instance_id))
        sys.exit(0)

    for inst_id,data in instance_data.items():
        name = data['name']
        state = data['state']
        public_ip = data['public_ip']
        if DEBUG:
            print("Instance (%s) state: %s" % (inst_id, state) )

        if input_args.stop:
            if state == 'stopped':
                print("WARNING - Instance is already in state=%s" % (state))
            else:
                state = stop_instance(ec2, inst_id)

        elif input_args.start:
            if state == 'stopped':
                state = start_instance(ec2, inst_id)
            else:
                print("WARNING - Instance is currently in state=%s" % (state))
                sys.exit(0)

        else:
            print("Instance-id (%s); Name=(%s) STATE: %s" % (inst_id, name, state))
            if state != 'stopped':
                print("PUBLIC-IP: %s" % (public_ip))


sys.exit(0)

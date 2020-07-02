#!/usr/bin/env python
"""

  File: S3_manager.py
  Description:
    Exposes Bucket() and Object() classes for managing AWS-S3 resources with boto3.
    While many more operations on these resources exist, these two classes will
    demonstrate the primary S3 management capabilities.  For more see:
    https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html
  Author: Bill Fanselow 2020-07-02

  Requires:
    pip install boto3
    pip install decorator

  ~~~~~~~~~~~~~~~~~~~~~~~~~~
  AWS-S3 NOTES:
    SUMMARY:
      AWS S3 stores data as "Objects" within "Buckets" - Buckets are containers for Objects.
      An object is a file and any optional metadata that describes the file.  An object can be
      any kind of file: a text file, a photo, a video, etc.  You can specify the geographical
      Region where S3 will store the bucket and its contents.

    FILENAMES:
      S3 uses the file prefix to map it onto a partition. Performance issues can arise
      from adding too many files with the same prefix (all getting assigned to the same
      partition).  By adding randomness to your file names, you can efficiently distribute
      your data within an S3 bucket.

    ACLs:
      Access-control-lists (ACL's) can be configured on Buckets and Objects to control
      who can create, delete, and list objects in it and to control what access is
      availalbe to specific objects.  As a general rule, AWS recommends using S3 bucket
      "policies" or IAM policies for access control as S3 ACLs are a legacy access control
      mechanism that predates IAM. When a request is made to S3, the authorization decision
      depends on the union of all the IAM policies, S3 bucket policies, and S3 ACLs that apply.

    ENCRYPTION:
      You can protect your data using encryption. The simplest is server-side encryption using the
      AES-256 algorithm where AWS manages both the encryption and the keys.

    STORAGE-TYPE:
      Each object in Amazon S3 has a storage class associated with it. Each class provides different
      tradeoffs between cost and availablity depending on how the data is used.

    VERSIONING
      You can use versioning to keep a complete record of your objects over time. This provides some
       protection mechanism against accidental deletion of your objects. When you request a versioned
       object, Boto3 will retrieve the latest version. Again, there is a tradeoff with cost.  When
       you add a new version of an object, the storage that object takes in total is the sum of the
       size of its versions. So if you’re storing 10 versions of a 1GB you will be charged for 10GB
       of storage.
  ~~~~~~~~~~~~~~~~~~~~~~~~~~

  TODO:
   1) Add configuration of credentials to override default boto3 behavior.
   2) Fill out methods for traversal of Objects

"""

#------------------------------------------------------------------------------
import os
import sys
import uuid
import boto3
from decorator import decorator
from botocore.client import ClientError

DEBUG = 2

#------------------------------------------------------------------------------
class MethodDecorators(object):
  @decorator
  def check_bucket_exists(func, self, bucket_name, *args, **kwargs):
      """ Ensure the bucketname exists before peforming bucket operations"""
      if not self.bucket_exists(bucket_name):
          print("%s: Bucket (%s) does NOT exist or is inaccessible" % (self.cname, bucket_name))
          return None
      else:
          return func(self, bucket_name, *args, **kwargs)

#------------------------------------------------------------------------------
class AWSResource():
    """ Parent class for generic S3 resource management """

    def __init__(self, d_init_args=None):

        self.cname = self.__class__.__name__
        self.credentials = {}  # placeholder for managing credentials

        self.session = boto3.session.Session()
        self.region = self.session.region_name

        self.client = boto3.client('s3')
        self.resource = boto3.resource('s3')

        self.debug = DEBUG
        if d_init_args:
            self.debug = d_init_args.get('debug', DEBUG)


    def gen_uniq_name(self, prefix, char_limit=32):
        """ Generate a name by concatenating passed prefix with semi-random suffix. 
        AWS-S3 constraints mandate only lowercase letters are allowed so we force 
        lc-translation.
         Args:
          * (str) prefix
          * (int) OPTIONAL character limit > 2
         Return: (str) random name
        """
        if char_limit < 2:
            char_limit = 32
        random_suffix = uuid.uuid4().hex[:char_limit]
        name = prefix.lower() + random_suffix
        return name

    def dprint(self, level, msg):
        """Internal debug message printing"""
        if level <= self.debug:
            print("%s: (%d) %s" % (self.cname, level, msg))


#------------------------------------------------------------------------------
class S3Bucket(AWSResource):
    """S3 Bucket class"""

    def __init__(self, d_init_args=None):

        super().__init__(d_init_args)

        self.cname = self.__class__.__name__
        self.bucket_list = []


    def bucket_exists(self, bucket_name):
        """ Quick/cheap way to identify if a bucket exists """
        try:
            self.client.head_bucket(Bucket=bucket_name)
            return True
        except ClientError:
            # The bucket does not exist or you have no access.
            return False


    def get_all_names(self):
        """ Rerieve a list of all bucket names """
        names = [ bucket.name for bucket in self.resource.buckets.all() ]
        return names


    def list_all(self):
        """ Output list of all bucket names """
        for i,name in enumerate(self.get_all_names(), start=1):
            print( "%d) %s" % (i, name) )


    def list_common_prefixes(self, bucket_name, delim="/"):
        """ List all common bucket-name prfixes. This is important method as
         S3 uses the file prefix to map it onto a partition. Performance issues can
         arise from adding too many files with the same prefix (all getting assigned
         to the same partition).
        Args:
          * (str) bucket-name
          * (str) OPTIONAL delimter string
        """
        paginator = self.client.get_paginator('list_objects')
        result = paginator.paginate(Bucket=bucket_name, Delimiter=delim)
        for prefix in result.search('CommonPrefixes'):
            print(prefix.get('Prefix'))


    def create_new_bucket(self, bucket_name_prefix, region=None):
        """ Create a new bucket. Name will be created with random suffix, as
         bucket names are DNS compliant and must be unique.
        Args:
         * (str) bucket name prefix
         * (str) OPTIONAL AWS region (default=self.region)
        Retuns: (obj) newly created bucket
        """
        if not region:
            region = self.region

        bucket_name = self.gen_uniq_name(bucket_name_prefix)
        self.dprint(1, "Creating new bucket (%s)" % (bucket_name))

        bucket = None
        try:
            bucket = self.resource.create_bucket(Bucket=bucket_name,
                          CreateBucketConfiguration={ 'LocationConstraint': region })
        except Exception as e:
            # placeholder to do something
            raise

        return bucket


    @MethodDecorators.check_bucket_exists
    def empty_bucket(self, bucket_name):
        """ Empty a bucket - removing all objects.
        Args:
         * (str) bucket name
        Retuns: (dict) operation results
        """
        resp = None
        self.dprint(1, "Emptying bucket (%s)" % (bucket_name))
        bucket = self.resource.Bucket(bucket_name)
        try:
            resp = bucket.objects.delete()
        except Exception as e:
            # placeholder to do something
            raise

        self.dprint(1, "RESP-empty_bucket(): %s" % resp)
        return resp


    @MethodDecorators.check_bucket_exists
    def delete_bucket(self, bucket_name):
        """ Delete a bucket after removing all objects.
        Args:
         * (str) bucket name
        Retuns: (dict) operation results
        """

        ## First we empty the bucket
        resp_empty = self.empty_bucket(bucket_name)

        self.dprint(1, "Deleting bucket (%s)" % (bucket_name))
        resp = None
        bucket = self.resource.Bucket(bucket_name)
        try:
            resp = bucket.delete()
        except Exception as e:
            # placeholder to do something
            raise

        self.dprint(1, "RESP-delete_bucket(): %s" % resp)
        return resp


    def delete_all(self, verify=1):
        """ Delete all buckets after removing all objects. BE CAREFUL WITH THIS!!!
         Default access to this method involves user-verification.
        """
        resp = None
        bnames = self.get_all_names()
        N = len(bnames)
        if N:
            ans = 'y'
            if verify:
                ans = input("Are you sure you want to remove all %d buckets?: [y|n] " % N)
            if ans.strip().lower() == 'y':
                for name in bnames:
                    resp = self.delete_bucket(name)
        else:
            print("%s: Zero buckets found" % (self.cname))


    @MethodDecorators.check_bucket_exists
    def push_file(self, bucket_name, filename, **kwargs):
        """ Push/upload a (file) object to a specified bucket-name.
         Args:
          * (str) bucket-name
          * (str) file-name to upload
          * (kwargs) for ExtraArgs
         Return: (obj) response

         NOTE: Upload can be perfomed using either the S3 Bucket() or Object() object.
          For simplicity here, we will use the Object() object.

         ExtraArgs Examples:
          * ACL's:      ExtraArgs={'ACL': 'public-read'}
          * Encryption: ExtraArgs={'ServerSideEncryption': 'AES256'}
          * Storage:    ExtraArgs={'StorageClass': 'STANDARD_IA'}

        """
        resp = None
        self.dprint(1, "Pushing file (%s) to bucket (%s). Extra=(%s)" % (filename, bucket_name, str(kwargs)))
        d_extra = kwargs
        try:
            resp = self.resource.Object(bucket_name, filename).upload_file( Filename=filename, ExtraArgs=d_extra)
        except Exception as e:
            # placeholder to do something
            raise

        self.dprint(1, "RESP-upload_file(): %s" % resp)
        return resp


    @MethodDecorators.check_bucket_exists
    def pull_file(self, bucket_name, filename, local_dest_path):
        """ Pull/download a (file) object from a specified bucket-name.
         Args:
          * (str) bucket-name
          * (str) file-name to download
          * (str) local path to which file is downloaded
         Return: (obj) response
        """
        resp = None
        self.dprint(1, "Downloading file (%s) from bucket (%s) to localhost:%s" % (filename, bucket_name, local_dest_path))
        try:
            resp = self.resource.Object(bucket_name, filename).download_file( Filename=local_dest_path )
        except Exception as e:
            # placeholder to do something
            raise

        self.dprint(1, "RESP-download_file(): %s" % resp)
        if not os.path.exists(local_dest_path):
            print("ERROR - File download failed - local file not found: %s" % (dest_path))
            
        return resp


    def copy_file(self, bucket_name_source, bucket_name_dest, filename):
        """ Copy file from one bucket to another
         Args:
          * (str) source bucket-name
          * (str) destination bucket-name
          * (str) file-name to copy
         Return: (obj) response
        """
        resp = None
        if not self.bucket_exists(bucket_name_source):
            print("%s: Source bucket (%s) does not exist or is inaccessible" % (self.cname, bucket_name_souce))
            return None
        if not self.bucket_exists(bucket_name_dest):
            print("%s: Destination bucket (%s) does not exist or is inaccessible" % (self.cname, bucket_name_dest))
            return None

        copy_source = { 'Bucket': bucket_name_source, 'Key': filename }
        self.dprint(1, "Copying file (%s) from bucket (%s) to bucket (%s)" % (filename, bucket_name_source, bucket_name_dest))
        try:
            resp = self.resource.Object(bucket_name_dest, filename).copy(copy_source)
        except Exception as e:
            # placeholder to do something
            raise

        self.dprint(1, "RESP-copy_file(): %s" % resp)
        return resp


    @MethodDecorators.check_bucket_exists
    def remove_file(self, bucket_name, filename):
        """ Remove file from a bucket
         Args:
          * (str) bucket-name
          * (str) file-name to remove
         Return: (obj) response
        """
        resp = None
        self.dprint(1, "Removing file (%s) from bucket (%s)" % (filename, bucket_name))
        try:
            resp = self.resource.Object(bucket_name, filename).delete()
        except Exception as e:
            # placeholder to do something
            raise

        self.dprint(1, "RESP-delete_file(): %s" % resp)
        return resp


    @MethodDecorators.check_bucket_exists
    def get_file_acls(self, bucket_name, filename):
        """ Check file ACL
         Args:
          * (str) bucket-name
          * (str) file-name to check
         Return: (obj) response
        """
        print("%s: Getting ACLs for file=(%s) in bucket=(%s)" % (self.cname, filename, bucket_name))
        acls = self.resource.Object(bucket_name, filename).Acl()
        return acls


    @MethodDecorators.check_bucket_exists
    def get_file_grants(self, bucket_name, filename):
        """ Check file grants
         Args:
          * (str) bucket-name
          * (str) file-name to check
         Return: (obj) response
        """
        print("%s: Getting grants for file=(%s) in bucket=(%s)" % (self.cname, filename, bucket_name))
        grants = self.resource.Object(bucket_name, filename).Acl().grants
        return grants


    @MethodDecorators.check_bucket_exists
    def set_file_acls(self, bucket_name, filename, acl_value):
        """ Set file ACL
         Args:
          * (str) bucket-name
          * (str) file-name to set ACL on
          * (str) ACL value to apply
         Return: (obj) response
        """
        print("%s: Setting file ACL=(%s) on file=(%s) in bucket=(%s)" % (self.cname, acl_value, filename, bucket_name))
        acls = self.resource.Object(bucket_name, filename).Acl().put(ACL=acl_value)
        return acls


    @MethodDecorators.check_bucket_exists
    def enable_bucket_versioning(self, bucket_name):
        """ Enable bucket-versioning on a bucket """
        print("%s: Enabling bucket-versioning for (%s)" % (self.cname, bucket_name))
        bkt_versioning = self.resource.BucketVersioning(bucket_name)
        bkt_versioning.enable()
        status = bkt_versioning.status
        return status


#------------------------------------------------------------------------------
class S3Object(AWSResource):
    """S3 Object class"""

    def __init__(self, d_init_args=None):

        super().__init__(d_init_args)

        self.cname = self.__class__.__name__
        self.credentials = {}
        self.bucket_list = []

    def list_all(self):
        """ Output list of all bucket names """
        for i,bucket in enumerate(self.resource.buckets.all(), start=1):
            print( "%d) %s" % (i, bucket.name) )
            for j,item in enumerate(bucket.objects.all(), start=1):
                print("\t(%d) %s" % (j, item.key))


    def get_parent_bucket(self, object):
        """ Return the Bucket andme hodling passed Object """
        bucket = object.Bucket()
        return bucket


#------------------------------------------------------------------------------
if __name__ == '__main__':

    import time

    s3bkt = S3Bucket()

    s3bkt.delete_all()
    s3bkt.list_all()

    bkt_name_prefix = 'billF.test2' # prefix only - suffix gets added

    # Create two buckets
    bucket1 = s3bkt.create_new_bucket(bkt_name_prefix)
    bname1 = bucket1.name
    print(bname1)
    bucket2 = s3bkt.create_new_bucket(bkt_name_prefix)
    bname2 = bucket2.name
    print(bname2)
    print("-"*40)
    time.sleep(3)

    # Create temp file
    filename = s3bkt.gen_uniq_name('bills-tempfile', 6)
    content = 'This is some file content'
    with open(filename, 'w') as f:
        f.write(content)
    f.close()

    # Push (upload) file to bucket1
    resp = s3bkt.push_file(bname1, filename)
    if resp:
        print(resp)
    print("-"*40)
    time.sleep(3)

    # Get file ACL's for filename in bucket1
    facl = s3bkt.get_file_acls(bname1, filename)
    if facl:
        print(facl)
    print("-"*40)
    time.sleep(3)

    # Set file ACL=private for filename in bucket1
    facl = s3bkt.set_file_acls(bname1, filename, 'private')
    if facl:
        print(facl)
    print("-"*40)
    time.sleep(3)

    # Get file grants for filename in bucket1
    grants = s3bkt.get_file_grants(bname1, filename)
    if grants:
        print(grants)
    print("-"*40)
    time.sleep(3)


    # Instantiate S3Object and list all objects in all buckets
    print("All objects:")
    s3obj = S3Object()
    s3obj.list_all()
    print("-"*40)
    time.sleep(3)


    # Copy file from bucket1 to bucket2
    resp = s3bkt.copy_file(bname1, bname2, filename)
    if resp:
        print(resp)
    print("-"*40)
    time.sleep(3)

    # Remove file from bucket1
    resp = s3bkt.remove_file(bname1, filename)
    if resp:
        print(resp)
    print("-"*40)
    time.sleep(3)


    # Pull (download) file from bucket2
    dest_path = "/tmp/" + filename
    resp = s3bkt.pull_file(bname2, filename, dest_path)
    if resp:
        print(resp)
    print("-"*40)
    time.sleep(3)

    # Delete contents of bucket1
    resp = s3bkt.empty_bucket(bname1)
    if resp:
        print(resp)
    print("-"*40)
    time.sleep(3)

    # Delete bucket-contents and Bucket for both
    resp = s3bkt.delete_bucket(bname1)
    if resp:
        print(resp)
    resp = s3bkt.delete_bucket(bname2)
    if resp:
        print(resp)
    print("-"*40)
    time.sleep(3)

    ## list again
    s3bkt.list_all()

"""

  Script: sample_auto_config.py

  This script is a template for script that pull EC2 meta-data and perform
  an automatic app-config setting with that data.

  Steps:
    1) Get EC2 instance Meta data from the local EC2 instance by making a
       request to: http://169.254.169.254/latest/meta-data/<data-method>
    2) Perform the auto-config setting

  Requires: pip install requests

  data-methods:
    * ami-id
    * ami-launch-index
    * ami-manifest-path
    * block-device-mapping/
    * events/
    * hostname
    * identity-credentials/
    * instance-action
    * instance-id
    * instance-type
    * local-hostname
    * local-ipv4
    * mac
    * metrics/
    * network/
    * placement/
    * profile
    * public-hostname
    * public-ipv4
    * public-keys/
    * reservation-id
    * security-groups

"""

import requests

meta_data_url = 'http://169.254.169.254/latest/meta-data/'

#---------------------------------------------------------------
def get_data(data_method):
    """Retieve and return the value assocated with data-method request"""
    value = None
    request_url = meta_data_url + data_method
    try:
        value = requests.get(
            request_url,
            timeout=0.01).text
    except requests.exceptions.RequestException:
        raise

    return value
#---------------------------------------------------------------
def configure(value, **kwargs):
    """Take the passed value and perform a local app config update"""
    key = kwargs.get('key', None)
    print("Setting value: %s=%s" % (key, value))
    # implement as needed

#---------------------------------------------------------------
if __name__ == '__main__':
    """Simple example of getting pub-ip"""
    method = 'public-ipv4'
    pub_ip = get_data(method)
    configure(pub_ip, key=method)

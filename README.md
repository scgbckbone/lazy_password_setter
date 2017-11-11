# Lazy password setter

##### Simple command line utility for changing passwords over ssh.

###### For now, only KeePass password manager is supported.

###### Installation:
```
git clone https://github.com/scgbckbone/lazy_password_setter.git
virtualenv env_name --python=python2.7
source env_name/bin/activate
python setup.py install
```

###### What it needs:
* KeePass
* config file

Config file has to be python module and has to have following attributes:
* username [str] or None
* password [str] or None
* first_run [bool]
    are you running for a first time, with no inputs in keepass?
* port [str]
* password_len [int]
    # length of new passwords to be generated
* connections [dict]
    # Can be an empty dict if 'first_run' is False and credentials are
    # already in KeePass. Or 'first_run' is True, yet 'use_ssh_config'
    # is True. Else:
    # { 'username@host:port': 'current_pwd' }
    # if you have same username for all - you can fill 'username' and
    # dict can look like this (same applies to port and password)
    # same username: { 'host:port': 'current_pwd' }
    # same username and port for all: { 'host': 'current_pwd' }
* ssh_host_pwd_map [dict]
    # Can be empty dict if 'first_run' is False or 'first_run' is True
    # yet 'connections' are specified and 'use_ssh_config' is False
    # specify only those host name that you'd like to change
    # { 'hostname': 'current_pwd' }
* ssh_config_keys [tuple]
    # specify keys from config file to be parsed
    # In most cases - copy default
    # default: ('HostName', 'User', 'Port', 'IdentityFile')
* use_ssh_config [bool]
    # whether or not to use ssh config file
    #
* ssh_config_path [str] or None
    # path to your ssh config file
* keepass_db_path [str]
    # path to your '.kdbx' database file
* keepass_pwd [str]
    # pass-phrase for your '.kdbx' database file


```python
# 
username = None

#
password = None
# 
first_run = True
#
port = "22"
#
password_len = 25
#
connections = {}
#
ssh_host_pwd_map = {}
# Keys that are read by ssh Config Parser
ssh_config_keys = ('HostName', 'User', 'Port', 'IdentityFile')
# 
use_ssh_config = False
# path to your ssh config
ssh_config_path = None
# path to your '.kdbx' database file
keepass_db_path = None
# password for '.kdbx' database file
keepass_pwd = None
```
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

Config file has to be python module that has following attributes:

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
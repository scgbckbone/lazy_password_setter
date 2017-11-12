# Lazy password setter

##### Simple command line utility for changing passwords over ssh.

###### For now, only KeePass password manager is supported.

#### Implementation details:
  * this package is wrapped around fabric that is wrapped around paramiko
  * passwords are changed via here string so [no worries about process table](https://stackoverflow.com/questions/47042953/how-dangerous-is-to-echo-passwords-via-pipe-to-passwd)

###### Installation:
```
git clone https://github.com/scgbckbone/lazy_password_setter.git
virtualenv env_name --python=python2.7
source env_name/bin/activate
python setup.py install
```
Then you should have 'changepwds' command available via your command line.
```
changepwds --help
```

###### What it needs:
###### KeePass
###### config file

Config file has to be python module and has to have following attributes:
###### username [str] or None
###### password [str] or None
###### first_run [bool]
  * are you running for a first time, with no inputs in keepass?
###### port [str]
###### password_len [int]
  * length of new passwords to be generated
###### connections [dict]
  * Can be an empty dict if 'first_run' is False and credentials are
  * already in KeePass. Or 'first_run' is True, yet 'use_ssh_config'
  * is True. Else:
  * { 'username@host:port': 'current_pwd' }
  * if you have same username for all - you can fill 'username' and
  * dict can look like this (same applies to port and password)
  * same username: { 'host:port': 'current_pwd' }
  * same username and port for all: { 'host': 'current_pwd' }
###### ssh_host_pwd_map [dict]
  * Can be empty dict if 'first_run' is False or 'first_run' is True
  * yet 'connections' are specified and 'use_ssh_config' is False
  * specify only those host name that you'd like to change
  * { 'hostname': 'current_pwd' }
###### ssh_config_keys [tuple]
  * specify keys from config file to be parsed
  * In most cases - copy default
  * default: ('HostName', 'User', 'Port', 'IdentityFile')
###### use_ssh_config [bool]
  * whether or not to use ssh config file
###### ssh_config_path [str] or None
  * path to your ssh config file
###### keepass_db_path [str]
  * path to your '.kdbx' database file
###### keepass_pwd [str]
  * pass-phrase for your '.kdbx' database file


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

# Examples

I'm running this for a first time and do not want to use my ssh config file.
  * I do not have same username and password for each remote host
  * I do not have any folder in my keepass with name 'servers'
  * I only use port 22
  * i want generated passwords to be 50 characters long
  * my '.kdbx' file is in /home/peter/Passwords.kdbx
  
here is my config file that I have in /home/peter/my_conf.py:
  
```python
first_run = True
password_len = 50
port = "22"
connections = {
    "username@host_name": "my_current_password1",
    "user@host1_name": "my_current_password2",
    "name@host2_name": "my_current_password3",
    "username@host3_name": "my_current_password4",
}
keepass_db_path = "/home/peter/Passwords.kdbx"
keepass_pwd = "secret_keepass_password"
```
and run it:
```bash
changepwds -c /home/peter/my_conf.py

or 

changepwds --config=/home/peter/my_conf.py
```

If I'm running for a first time, yet want to use my ssh config file.
(with all four above mentioned conditions)
  * my ssh config file is in /home/peter/.ssh/config

config file:

```python
first_run = True
password_len = 50
port = "22"
# keys have to match to your HOST from ssh config file
# config will be read whole, but only host specified in 'ssh_host_pwd_map
# will be subjected to change
ssh_host_pwd_map = {
    "host_name": "my_current_password1",
    "host1_name": "my_current_password2",
    "host2_name": "my_current_password3",
    "host3_name": "my_current_password4",
}
use_ssh_config = True
ssh_config_path = "/home/peter/.ssh/config"
keepass_db_path = "/home/peter/Passwords.kdbx"
keepass_pwd = "secret_keepass_password"
```

and run.

If you already have data in KeePass only thing that you need to set is:
  * I decided that 50 characters is too much. 25 is enough.
  
```python
first_run = False
password_len = 25
```

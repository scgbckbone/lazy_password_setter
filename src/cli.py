import os
import imp
import click
from config import config as config_f
from log_facility import get_me_logger
from run import main, handle_exceptions


here = os.path.abspath(__file__)
here_lst = here.split(os.sep)
conf = os.sep.join(here_lst[:-2]) + os.sep + "config" + os.sep + "config.py"
log_path = os.sep.join(here_lst[:-2]) + os.sep + "log"


logger = get_me_logger(
    'cli_logger',
    log_path + os.sep + 'base.log',
    stream=False
)

help_msg = "Provide full path to your config file."


@click.command()
@click.option('--config', '-c', default=None, help=help_msg)
def change_pwds(config):
    """
    'changepwds' command just makes your f***ing life easier.
    Create config file and let it run.

    Config file has to be python module and has to have following attributes:
        * username [str] or None
        * password [str] or None
        * first_run [bool]
            # are you running for a first time, with no inputs in keepass?
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
    """
    if not config:
        click.echo(help_msg)
        return
    try:
        user_config = imp.load_source('config', config)
    except IOError as e:
        click.echo("File %s not found." % config)
        logger.error("Invalid path to config file: %s" % e)
    except Exception as e:
        click.echo("Ooups. Something went wrong.")
        click.echo(e)
        logger.critical("%s" % e)
    else:
        for i in dir(config_f):
            if not i.startswith("__"):
                try:
                    user_config.__dict__[i]
                except KeyError:
                    user_config.__dict__[i] = config_f.__dict__[i]
        handle_exceptions(main, user_config)


if __name__ == "__main__":
    change_pwds()

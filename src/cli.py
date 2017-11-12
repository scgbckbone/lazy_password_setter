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
    'changepwds' command changes your passwords on remote hosts
    via ssh.
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

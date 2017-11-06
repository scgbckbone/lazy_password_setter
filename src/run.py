import os
import pprint
from fabric.api import env
from fabric.network import ssh
from fabric_pwd_util import FabricPasswordUtility
from keepass_manager import KPManager
from fabfile import PWDChanger, FabricException
from config import config as config_f
from config_parser import ConfigParser
from log_facility import get_me_logger


here = os.path.abspath(__file__)
here_lst = here.split(os.sep)
log_path = os.sep.join(here_lst[:-2]) + os.sep + "log"

env.abort_exception = FabricException

logger = get_me_logger(
    'base_logger',
    log_path + os.sep + 'base.log',
    stream=True
)


def handle_exceptions(func, *args, **kwargs):
    try:
        func(*args, **kwargs)
    except UnicodeDecodeError as e:
        logger.error(e.args)
        print("Save your database file before processing.")
    except (AssertionError, IOError) as e:
        logger.error(e.args)
        print("Database file path not provided or incorrect.")
    except Exception as e:
        logger.error(e.args)
        print(e.args)
    finally:
        print("BYE")


def notifier(func):
    success_msg = "Successfully changed passwords [host: new password]:\n"
    failure_msg = "\nFailed to change passwords [host: new password]:\n"
    pwd_log = open(log_path + os.sep + 'secret.txt', 'w')
    try:
        success, failure = func()
        print(success_msg)
        pwd_log.write(success_msg)
        pprint.pprint(success)
        pprint.pprint(success, stream=pwd_log)
        print(failure_msg)
        pprint.pprint(failure)
        pwd_log.write(failure_msg)
        pprint.pprint(failure, stream=pwd_log)
        print("\nSaving to KeePass...")
        print("Failed passwords will be saved in their original form.")
        print("Changed passwords will be saved in their new form.")
        return success, failure
    except Exception as e:
        pass
    finally:
        pwd_log.close()


def main(config):
    if config.first_run:
        if not config.connections and not config.use_ssh_config:
            print("Empty connections. Please specify it in config/config.py")
            return
        if not config.ssh_host_pwd_map and config.use_ssh_config:
            print("Empty pwd host map. Please specify it in config/config.py")
            return
    if config.use_ssh_config and not config.ssh_config_path:
        print("Provide path to your ssh config file in config/config.py.")
        return
    if config.use_ssh_config:
        env.use_ssh_config = True
        ssh_config = ConfigParser(config.ssh_config_path)

    ssh.util.log_to_file(log_path + os.sep + "paramiko.log", 10)

    keepass = KPManager(config.keepass_db_path, password=config.keepass_pwd)

    if config.first_run:
        keepass.first_run_check()
        fpu = FabricPasswordUtility(
            config.ssh_host_pwd_map if config.use_ssh_config else config.connections,
            username=config.username,
            password=config.password,
            port=config.port,
            pwd_len=config.password_len,
            ssh=config.use_ssh_config
        )
        new_passwords = fpu.new_connection_map()

        if config.use_ssh_config:
            pwd_changer = PWDChanger(
                actual_pwd_map=config.ssh_host_pwd_map,
                new_pwd_map=new_passwords,
                host_list=ssh_config.connection_obj.keys()
            )
            success, failure = notifier(pwd_changer.change_all_ssh)
            success.update(failure)

            keepass.add_all_ssh(success, ssh_config.connection_obj)
            keepass.save_changes()
        else:
            pwd_changer = PWDChanger(
                actual_pwd_map=fpu.connections,
                new_pwd_map=new_passwords,
                host_list=fpu.get_env_hosts_for_fabric()
            )
            success, failure = notifier(pwd_changer.change_all)

            success.update(failure)
            keepass.add_all(success)
            keepass.save_changes()

    else:
        keepass.find_or_create_server_group(find_only=True)
        if config.use_ssh_config:
            connection_obj = keepass.build_connection_map_from_entries(
                ssh_conf=True
            )
            fpu = FabricPasswordUtility(
                connection_obj, pwd_len=config.password_len,
                ssh=config.use_ssh_config
            )
            new_passwords = fpu.new_connection_map()
            pwd_changer = PWDChanger(
                actual_pwd_map=fpu.connections,
                new_pwd_map=new_passwords,
                host_list=ssh_config.connection_obj.keys()
            )
            success, failure = notifier(pwd_changer.change_all_ssh)
            keepass.delete_server_group()
            success.update(failure)
            keepass.add_all_ssh(success, ssh_config.connection_obj)
            keepass.save_changes()

        else:
            connection_obj = keepass.build_connection_map_from_entries()
            # check that input are in the kp
            fpu = FabricPasswordUtility(
                connection_obj, pwd_len=config.password_len
            )
            new_passwords = fpu.new_connection_map()
            pwd_changer = PWDChanger(
                actual_pwd_map=fpu.connections,
                new_pwd_map=new_passwords,
                host_list=fpu.get_env_hosts_for_fabric()
            )

            success, failure = notifier(pwd_changer.change_all)

            # delete old servers group
            keepass.delete_server_group()

            # merge success and failure and save it to kp
            success.update(failure)
            keepass.add_all(success)
            keepass.save_changes()


if __name__ == "__main__":
    handle_exceptions(main, config_f)


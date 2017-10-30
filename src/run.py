import os
import pprint
from fabric.api import env
from fabric.network import ssh
from fabric_pwd_util import FabricPasswordUtility
from keepass_manager import KPManager
from fabfile import PWDChanger, FabricException
from config import config
from config_parser import ConfigParser


here = os.path.abspath(__file__)
here_lst = here.split(os.sep)
log_path = os.sep.join(here_lst[:-2]) + os.sep + "log"

env.abort_exception = FabricException


def notifier(func):
        success, failure = func()
        print("Successfully changed passwords [host: new password]:")
        pprint.pprint(success)
        print("\nFailed to change passwords [host: new password]:")
        pprint.pprint(failure)
        print("\nSaving to KeePass...")
        print("Failed passwords will be saved in their original form.")
        print("Changed passwords will be saved in their new form.")
        return success, failure


def main():
    if not config.connections and config.first_run:
        print("Empty connections. Please specify it in config/config.py")
        return
    if config.use_ssh_config and not config.ssh_config_path:
        print("Provide path to your ssh config file.")
        return
    if config.use_ssh_config:
        env.use_ssh_config = True
        ssh_config = ConfigParser(config.ssh_config_path)

    ssh.util.log_to_file(log_path + os.sep + "paramiko.log", 10)

    keepass = KPManager(config.keepass_db_path, password=config.keepass_pwd)

    if config.first_run:
        keepass.first_run_check()
        fpu = FabricPasswordUtility(
            config.connections,
            username=config.username,
            password=config.password,
            port=config.port,
            pwd_len=config.password_len
        )
        new_passwords = fpu.new_connection_map()

        if config.use_ssh_config:
            new_host_pwd_map = ssh_config.create_new_host_pwd_map(
                new_passwords.values()
            )
            pwd_changer = PWDChanger(
                actual_pwd_map=config.ssh_host_pwd_map,
                new_pwd_map=new_host_pwd_map,
                host_list=ssh_config.connection_obj.keys()
            )
            pwd_changer.change_all_ssh()

            keepass.add_all_ssh(new_host_pwd_map, ssh_config.connection_obj)
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
        # not first run - working with keepass
        if config.use_ssh_config:
            pass
        else:
            # check that input are in the kp
            keepass.find_or_create_server_group(find_only=True)
            connection_obj = keepass.build_connection_map_from_entries()
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
    main()

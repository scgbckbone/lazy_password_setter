import os
import pprint
from fabric.api import env
from fabric.network import ssh
from fabric_pwd_util import FabricPasswordUtility
from keepass_manager import KPManager
from fabfile import PWDChanger
from config import config
from config_parser import ConfigParser


here = os.path.abspath(__file__)
here_lst = here.split(os.sep)
log_path = os.sep.join(here_lst[:-2]) + os.sep + "log"


def main():
    if not config.connections:
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
        fpu = FabricPasswordUtility(
            config.connections,
            username=config.username,
            password=config.password,
            port=config.port,
            pwd_len=25
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
            pwd_changer.change_all()

            keepass.add_all(new_passwords)

    else:
        # not first run - working with keepass
        pass



if __name__ == "__main__":
    main()



# ssh.util.log_to_file("paramiko.log", 10)
#
# env.passwords = {
#     'avirgovic@pip1-dev-ba.in.uptime.at:22': '5rFVChuEYp0cpuUjeg20',
#     'avirgovic@pip1-stg-ir.pipelinersales.com:22': 'Punishment0410!@--/w'
# }
# env.hosts = ['pip1-dev-ba.in.uptime.at', 'pip1-stg-ir.pipelinersales.com']
# env.user = "avirgovic"
#
#
# @task
# def cmd_run():
#     print("printing from fabric task")
#     raise NoUserNameError(
#         "Provide username, or adjust your connection object."
#         "conn object correct form:"
#         "\tusername@host:port"
#     )
#     run("uname")
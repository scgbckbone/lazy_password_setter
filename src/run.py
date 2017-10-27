import os
import pprint
from fabric.api import run, sudo, task, settings, env
from fabric.network import ssh
from fabric_pwd_util import FabricPasswordUtility
from keepass_manager import KPManager
from config import config


@task
def change_pwd():
    pass


def main():
    ssh.util.log_to_file("log/paramiko.log", 10)

    keepass = KPManager(config.keepass_db_path, password=config.keepass_pwd)

    if config.first_run:
        fpu = FabricPasswordUtility(
            config.connections,
            username=config.username,
            password=config.password,
            port=config.port,
            pwd_len=25
        )
        env.user = config.username
        env.hosts = fpu.get_env_hosts_for_fabric()
        env.passwords = fpu.new_connection_map()



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
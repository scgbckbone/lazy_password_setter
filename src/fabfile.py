from fabric.api import run, task, env, execute
from passlib.hash import sha512_crypt


class FabricException(Exception):
    """Fabric exception."""


@task
def change_pwd(oldpass, newpass):
    cmd = "echo -e '%s\\n%s\\n%s' | passwd" % (oldpass, newpass, newpass)
    run(cmd)


@task
def changepwd(username, pwd_hash):
    cmd = "echo '%s':'%s' | chpasswd -e" % (username, pwd_hash)
    run(cmd)


class PWDChanger(object):
    def __init__(self, host_list, actual_pwd_map, new_pwd_map):
        self.host_list = host_list
        self.actual_pwd_map = actual_pwd_map
        self.new_pwd_map = new_pwd_map

    @staticmethod
    def hash_pwd(pwd):
        hash_ = sha512_crypt.encrypt(pwd)
        return hash_

    @staticmethod
    def get_username_from_host(host_str):
        username, rest = host_str.split("@")
        return username

    def change_all(self):
        done = {}
        failed = {}
        for host, pwd in self.actual_pwd_map.iteritems():
            env.host_string = host
            env.password = pwd
            try:
                execute(
                    change_pwd,
                    oldpass=pwd,
                    newpass=self.new_pwd_map[host],
                )
            except FabricException:
                failed[host] = pwd
            else:
                done[host] = self.new_pwd_map[host]
        return done, failed

    def change_all_ssh(self):
        for host, pwd in self.actual_pwd_map.iteritems():
            execute(
                change_pwd,
                oldpass=pwd,
                newpass=self.new_pwd_map[host],
                host=host
            )


#
# if __name__ == "__main__":
#     ssh.util.log_to_file("paramiko.log", 10)
#     env.use_ssh_config = True
#     env.hosts = ["do"]
#
#
#     execute(
#         change_pwd,
#         oldpass="Punishment0410!@--/",
#         newpass="andrej123!@#",
#         host="do"
#     )

from fabric.api import run, task, env, execute, sudo
from passlib.hash import sha512_crypt
from pipes import quote


class FabricException(Exception):
    """Fabric exception."""


@task
def change_pwd_echo(oldpass, newpass):
    cmd = "echo -e '%s\\n%s\\n%s' | passwd" % (oldpass, newpass, newpass)
    run(cmd)


@task
def change_pwd_echo_chpasswd(username, pwd_hash):
    cmd = "echo '%s':'%s' | chpasswd -e" % (username, pwd_hash)
    sudo(cmd)


@task
def change_pwd_usermod_p(username, pwd_hash):
    cmd = "usermod -p '%s' '%s'" % (pwd_hash, username)
    sudo(cmd)


@task
def change_pwd_here_string(oldpass, newpass, escaped=False):
    cmd = "passwd <<< %s$'\\n'%s$'\\n'%s" % (oldpass, newpass, newpass)
    run(cmd)


@task
def change_pwd_printf(oldpass, newpass):
    cmd = "printf '%s\n%s\n%s' | passwd" % (oldpass, newpass, newpass)
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

    @staticmethod
    def proper_quoting(pwd):
        return quote(pwd)

    def change_all(self):
        done = {}
        failed = {}
        for host, pwd in self.actual_pwd_map.iteritems():
            env.host_string = host
            env.password = pwd
            try:
                execute(
                    change_pwd_here_string,
                    oldpass=self.proper_quoting(pwd),
                    newpass=self.proper_quoting(self.new_pwd_map[host]),
                )
            except FabricException:
                failed[host] = pwd
            else:
                done[host] = self.new_pwd_map[host]
        return done, failed

    def change_all_ssh(self):
        done = {}
        failed = {}
        for host, pwd in self.actual_pwd_map.iteritems():
            try:
                execute(
                    change_pwd_here_string,
                    oldpass=self.proper_quoting(pwd),
                    newpass=self.proper_quoting(self.new_pwd_map[host]),
                    host=host
                )
            except FabricException:
                failed[host] = pwd
            else:
                done[host] = self.new_pwd_map[host]
        return done, failed

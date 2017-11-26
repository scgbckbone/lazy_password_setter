from fabric.api import run, task, env, execute, sudo
from passlib.hash import sha512_crypt
from pipes import quote
from config import config


class FabricException(Exception):
    """Fabric exception."""


class InvalidMethodOptionError(Exception):
    """Unsupported password change method."""


@task
def change_pwd_usermod_p(username, pwd_hash):
    cmd = "usermod -p '%s' '%s'" % (pwd_hash, username)
    sudo(cmd)


@task
def change_pwd_here_string(oldpass, newpass):
    cmd = "passwd <<< %s$'\\n'%s$'\\n'%s" % (oldpass, newpass, newpass)
    run(cmd)


class PWDChanger(object):

    options = {
        "here_string": change_pwd_here_string,
        "usermod_p": change_pwd_usermod_p,
    }

    def __init__(self, host_list, actual_pwd_map, new_pwd_map, ssh_config=None):
        self.host_list = host_list
        self.actual_pwd_map = actual_pwd_map
        self.new_pwd_map = new_pwd_map
        self.ssh_config = ssh_config
        self.method = self.choose_method_option()

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

    @staticmethod
    def make_kwargs_map(arg1, arg2):
        if config.method == "here_string":
            return {"oldpass": arg1, "newpass": arg2}
        elif config.method == "usermod_p":
            return {"username": arg1, "pwd_hash": arg2}

    def choose_method_option(self):
        if config.method not in self.options:
            raise InvalidMethodOptionError("Incorrect method option.")
        if config.method == "usermod_p":
            raise NotImplementedError("Not implemented.")
        return self.options[config.method]

    def change_all(self):
        done = {}
        failed = {}
        for host, pwd in self.actual_pwd_map.iteritems():
            env.host_string = host
            env.password = pwd
            try:
                execute(
                    task=self.method,
                    **self.make_kwargs_map(
                        self.proper_quoting(pwd),
                        self.proper_quoting(self.new_pwd_map[host]),
                    )
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
            if config.method == "usermod_p":
                user_name = self.ssh_config[host]["User"]
            try:
                execute(
                    task=self.method,
                    host=host,
                    **self.make_kwargs_map(
                        self.proper_quoting(pwd),
                        self.proper_quoting(self.new_pwd_map[host]),
                    )
                )
            except FabricException:
                failed[host] = pwd
            else:
                done[host] = self.new_pwd_map[host]
        return done, failed

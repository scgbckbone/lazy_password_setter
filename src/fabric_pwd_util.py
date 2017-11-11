import random
import string


class NoHostError(Exception):
    """If, no host is specified whn using ssh option."""


class NoUserNameError(Exception):
    """If no username is provided in both connections map and username param."""


class NoPasswordError(Exception):
    """If no password is provided in both connections map and password param."""


class MoreThanOneServersGroupError(Exception):
    """if there is more than one servers group outside recycle bin in KP"""


class FabricPasswordUtility(object):
    def __init__(self, connection_obj, username=None, port="22",
                 password=None, pwd_len=20, ssh=False):

        self.usr = username
        self.pwd = password
        self.connection_obj = connection_obj
        self.port = port
        self.ssh = ssh
        self.connections = self.check_and_correct_connections()
        self.pwd_len = pwd_len

    def check_and_correct_connections(self):
        if self.ssh:
            for host, pwd in self.connection_obj.items():
                if not host:
                    raise NoHostError("Specify host names.")
                if not pwd:
                    raise NoPasswordError(
                        "Provide password, or adjust your connection object."
                        "Connection object value: password"
                    )
            return self.connection_obj
        checked_conn_map = {}
        for key, value in self.connection_obj.iteritems():
            if "@" not in key and not self.usr:
                del checked_conn_map
                raise NoUserNameError(
                    "Provide username, or adjust your connection object."
                    "Connection object key correct form: \n"
                    "\t\tusername@host:port"
                )

            if not value and not self.pwd:
                del checked_conn_map
                raise NoPasswordError(
                    "Provide password, or adjust your connection object."
                    "Connection object value: password"
                )

            if ":" not in key:
                key = key + ":" + self.port
            if "@" not in key:
                key = self.usr + "@" + key
            if not value:
                value = self.pwd
            checked_conn_map[key] = value
        return checked_conn_map

    def new_connection_map(self):
        return dict(zip(
            self.connections.keys(),
            [self.generate_password() for _ in range(len(self.connections))]
        ))

    def get_env_hosts_for_fabric(self):
        return [i.split("@")[1].split(":")[0] for i in self.connections.keys()]

    def generate_password(self):
        chars = string.ascii_letters + string.digits + '!@#$%^&*"([{}])-=' + "'"
        rnd = random.SystemRandom()
        return ''.join(rnd.choice(chars) for _ in range(self.pwd_len))




import random
import string


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
        chars = string.ascii_letters + string.digits + '!@#$%^&*([{}])-='
        rnd = random.SystemRandom()
        return ''.join(rnd.choice(chars) for _ in range(self.pwd_len))

    @staticmethod
    def check_and_escape_single_quotes(pwd):
        if "'" in pwd:
            last_element = False
            first_element = False
            new_lst = list()
            res = pwd.split("'")
            if res[-1] == '':
                last_element = True
            if res[0] == '':
                first_element = True
            for i in range(len(res)):
                new_lst.append(res[i])
                if i != len(res) - 1:
                    new_lst.append("\\'")
            if last_element:
                new_lst.pop()
            if first_element:
                pass
            return "'".join(new_lst)
        else:
            return pwd


def xxx(pwd):
    new_str = ""
    res = pwd.split("'")
    for i in res:
        if i == '':
            new_str = new_str + "\\'"
        new_str = new_str + "'" + i + "'" + "\\'"
    return new_str


def yyy(pwd):
    indexes = []
    previous = 0
    for i in range(len(pwd)):
        if pwd[i] == "'":
            indexes.append((previous, i))
            previous = i
    indexes.append((previous, len(pwd)))
    print(indexes)
    for i in indexes:
        print(pwd[i[0]:i[1]])


def zzz(pwd, escape="\\'"):
    first = False
    last = False
    res = pwd.split("'")
    if res[0] == "":
        res.pop(0)
        first = True
    if res[-1] == "":
        last = True
        res.pop()
    new_str = ""
    for i in res:
        new_str = new_str + i + escape
    print(new_str)
    return new_str


if __name__ == "__main__":
    o = FabricPasswordUtility({}, ssh=True)
    passw = "'bozemoj'ja'to'jebem'dopice'"
    # new = "andrej123456"
    # x = o.check_and_escape_single_quotes(passw)
    # print(x)
    #
    # cmd = "passwd <<< 'andrej'$'\\n''%s'$'\\n''%s'" % (x, x)
    # print(cmd)
    # s = xxx(passw)
    # yyy(passw)
    zzz(passw)



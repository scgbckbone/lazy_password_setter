import os
from src.config_parser import ConfigParser


test_config = "test_config"
test_conf_path = os.getcwd() + os.sep + test_config


class ConfigTestUtil(object):

    def __init__(self, entry_no, path=None):
        self.entry_no = entry_no
        self.path = path if path else test_conf_path
        self.create_config(self.entry_no)

    @staticmethod
    def create_entry(host, url, user, port="22", identity_f="~/.ssh/sec"):
        entry = """\n
        HOST {}\n
        \t\tHostName {}\n
        \t\tUser {}\n
        \t\tPort {}\n
        \t\tIdentityFile {}\n""".format(
            host,
            url,
            user,
            port,
            identity_f
        )
        return entry

    def create_config(self, entry_no):
        with open(test_conf_path, "w") as f:
            for i in range(entry_no):
                f.write(
                    self.create_entry(
                        "test_host_{}".format(i),
                        "12{0}.1.{0}.1".format(i),
                        "test_user_{}".format(i)
                    )
                )

    def delete_test_config(self):
        os.remove(self.path)


def test_cp_01():
    try:
        o = ConfigParser("/home/blah/kokot")
    except Exception as e:
        assert e.message.startswith("File does not exist")


def test_cp_02():
    utility = ConfigTestUtil(10)
    o = ConfigParser(test_conf_path)

    assert o.exists
    assert isinstance(o.connection_obj, dict)
    assert len(o.connection_obj) == 10

    utility.delete_test_config()


def test_cp_03():
    f = open(test_conf_path, "w")
    f.write("nada sdjhfskdhf dasdjsklajd")

    o = ConfigParser(test_conf_path)

    assert not o.connection_obj

    f.close()
    os.remove(test_conf_path)




from config import config


class IntegrityError(Exception):
    """Configuration mismatch."""


class ConfigParser(object):
    def __init__(self, path):
        self.path = path
        self.exists = self.read_file()
        self.connection_obj = self.parse_config()

    def read_file(self):
        try:
            f = open(self.path, "r")
            f.close()
        except IOError:
            raise IOError("File does not exists or path is wrong.")
        else:
            return True

    def parse_config(self):
        main = dict()
        with open(self.path, "r") as f:
            cached_host = None
            for line in f.readlines():
                try:
                    key, value = line.strip().split()
                except ValueError:
                    continue
                if key == "HOST":
                    cached_host = value
                    main[value] = {}
                if key in config.ssh_config_keys:
                    main[cached_host][key] = value
        return main




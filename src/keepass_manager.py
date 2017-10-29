from pykeepass import PyKeePass


class MoreThanOneServersGroupError(Exception):
    """if there is more than one servers group outside recycle bin in KP"""


class KPManager(object):
    def __init__(self, kp_db_path, password):
        self.kp_db_path = kp_db_path
        self.password = password
        self.conn = self.init_connection()
        self.server_group = None
        self.rubbish = self.find_recycle_bin()

    def init_connection(self):
        try:
            kp = PyKeePass(self.kp_db_path, password=self.password)
        except IOError:
            raise
        except Exception as e:
            raise
        else:
            return kp

    def find_recycle_bin(self):
        rubbish = self.conn.find_groups_by_name("Recycle Bin", first=True)
        return rubbish

    def filter_trashed_server_groups(self, server_groups):
        server_groups_new = []
        for server_group in server_groups:
            if server_group.parentgroup.uuid == self.rubbish.uuid:
                continue
            server_groups_new.append(server_group)

        if len(server_groups_new) == 1:
            return server_groups_new[0]
        if len(server_groups_new) == 0:
            return None
        raise MoreThanOneServersGroupError(
            "More than one 'servers' group in KP. Delete old groups."
        )

    def find_or_create_server_group(self):
        server_group = self.filter_trashed_server_groups(
            self.conn.find_groups_by_name("servers")
        )
        if server_group:
            self.server_group = server_group
        else:
            server_group = self.conn.add_group(self.conn.root_group, "servers")
            self.conn.save()
            self.server_group = server_group

    def get_data_from_servers_group(self):
        conns = []
        for i in self.server_group.entries:
            conns.append(
                (i.username + "@" + i.url + ":" + "22", str(i.password))
            )
        return conns

    def build_connection_map_from_entries(self):
        return dict(self.get_data_from_servers_group())

    def parse_and_create_entry_map(self, key_val_pair):
        key, pwd = key_val_pair
        usr, url_port = key.split("@")
        url, port = url_port.split(":")
        return {
            "destination_group": self.server_group,
            "title": url.split(".")[0],
            "username": usr,
            "password": pwd,
            "url": url
        }

    def add_entry(self, entry):
        self.conn.add_entry(**entry)
        self.conn.save()

    def add_all(self, dict_obj):
        for entry in dict_obj.iteritems():
            entry = self.parse_and_create_entry_map(entry)
            self.add_entry(entry)

    def add_all_ssh(self, host_new_pwd, ssh_config_obj):
        for host, obj in ssh_config_obj.iteritems():
            try:
                host_name = obj["HostName"]
            except KeyError:
                host_name = host

            entry = {
                "destination_group": self.server_group,
                "title": host,
                "username": obj["User"],
                "password": host_new_pwd[host],
                "url": host_name,
                "notes": obj["IdentityFile"]
            }
            self.add_entry(entry)


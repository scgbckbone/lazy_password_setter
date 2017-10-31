from pykeepass import PyKeePass


class MoreThanOneServersGroupError(Exception):
    """if there is more than one servers group outside recycle bin in KP"""


class NoServerGroupError(Exception):
    """No server group was found to get data."""


class ServersGroupPresentError(Exception):
    """If first run, there should be no active server folders."""


class KPManager(object):
    def __init__(self, kp_db_path, password, testing=False):
        self.kp_db_path = kp_db_path
        self.password = password
        self.conn = self.init_connection()
        self.server_group = None
        self.rubbish = self.find_recycle_bin()
        self.testing = testing
        if self.testing:
            self.test_group = self.testing_configuration()

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

    def first_run_check(self):
        server_group = self.filter_trashed_server_groups(
            self.conn.find_groups_by_name("servers"),
            first_run=True
        )

    def filter_trashed_server_groups(self, server_groups, first_run=False):
        server_groups_new = []
        for server_group in server_groups:
            if server_group.parentgroup.uuid == self.rubbish.uuid:
                continue
            server_groups_new.append(server_group)

        if len(server_groups_new) == 1:
            if first_run:
                raise ServersGroupPresentError("Delete old servers group")
            return server_groups_new[0]
        if len(server_groups_new) == 0:
            return None
        raise MoreThanOneServersGroupError(
            "More than one 'servers' group in KP. Delete old groups."
        )

    def find_or_create_server_group(self, find_only=False):
        server_group = self.filter_trashed_server_groups(
            self.conn.find_groups_by_name("servers")
        )
        if server_group:
            self.server_group = server_group
        else:
            if find_only:
                raise NoServerGroupError("No server group.")
            server_group = self.conn.add_group(self.conn.root_group, "servers")
            self.server_group = server_group

    def testing_configuration(self):
        test_group = self.conn.add_group(self.conn.root_group, "test")
        return test_group

    def get_data_from_servers_group(self, ssh_conf):
        conns = []
        for i in self.server_group.entries:
            if ssh_conf:
                # TODO what if does not have title?
                key_val = i.title, str(i.password)
            else:
                key_val = (i.username + "@" + i.url + ":" + "22", str(i.password))
            conns.append(key_val)
        return conns

    def build_connection_map_from_entries(self, ssh_conf=False):
        return dict(self.get_data_from_servers_group(ssh_conf))

    def parse_and_create_entry_map(self, key_val_pair):
        key, pwd = key_val_pair
        usr, url_port = key.split("@")
        url, port = url_port.split(":")
        return {
            "destination_group": self.test_group if self.testing else self.server_group,
            "title": url.split(".")[0],
            "username": usr,
            "password": pwd,
            "url": url
        }

    def add_entry(self, entry):
        self.conn.add_entry(**entry)

    def add_all(self, dict_obj):
        self.find_or_create_server_group()
        for entry in dict_obj.iteritems():
            entry = self.parse_and_create_entry_map(entry)
            self.add_entry(entry)

    def add_all_ssh(self, host_new_pwd, ssh_config_obj):
        self.find_or_create_server_group()
        for host, obj in ssh_config_obj.iteritems():
            if host in host_new_pwd:
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

    def delete_group(self, group):
        self.conn.delete_group(group)

    def delete_server_group(self):
        self.conn.delete_group(self.server_group)

    def save_changes(self):
        self.conn.save()


if __name__ == "__main__":
    from config import config
    connections = {
        'avirgovic@lic1-stg-ir.pipelinersales.com:22': 'IqIQSgg5aUZEPv82%z87e8RHY',
        'avirgovic@pip1-dev-ba.in.uptime.at:22': 'fJNiDJZd6VXQo!iyj5%BRMh37',
        'avirgovic@pip1-stg-ir.pipelinersales.com:22': 'G*hK42^t*Q(CjZmMx0firycou',
        'avirgovic@pip2-stg-ir.pipelinersales.com:22': 'jHA^f)TkR96uE*W9Y4Ja^)8yJ'
    }
    kp = KPManager(config.keepass_db_path, config.keepass_pwd, testing=True)

    kp.add_all(connections)
    kp.save_changes()

    kp.delete_group(kp.test_group)

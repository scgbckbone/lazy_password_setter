import os


username = None

password = None

first_run = True

port = "22"

password_len = 20

connections = {}


conn_obj = {}

# using ssh config file
use_ssh_config = True
ssh_config_path = None

# ===========================KEEPASS============================================

keepass_db_path = os.environ.get("kpdb")

keepass_pwd = os.environ.get("kppwd")

import pytest
from src.fabric_pwd_util import (
    FabricPasswordUtility, NoPasswordError, NoUserNameError, NoHostError
)

conn_obj = {
    "skvele.sk": None,
    "127.0.0.1": None,
    "0.0.0.0": "fds%^&jkn",
}


def test_fpu_01():
    with pytest.raises(NoUserNameError) as exc_info:
        o = FabricPasswordUtility(
            connection_obj=conn_obj,
        )
    assert str(exc_info.value).startswith("Provide username")


def test_fpu_02():
    with pytest.raises(NoPasswordError) as exc_info:
        o = FabricPasswordUtility(
            connection_obj=conn_obj,
            username="andrej"
        )
    assert str(exc_info.value).startswith("Provide password")


def test_fpu_03():
    o = FabricPasswordUtility(
        connection_obj=conn_obj,
        username="andrej",
        password="secret"
    )
    assert isinstance(o.connections, dict)
    for host_str in o.connections:
        name, rest = host_str.split("@")
        assert name == o.usr
        host, port = rest.split(":")
        assert port == o.port
        assert host in conn_obj


def test_fpu_04():
    conn_obj_ = {"andrej": "secret"}
    o = FabricPasswordUtility(
        connection_obj=conn_obj_,
        username="andrej",
        password="secret",
        ssh=True
    )
    assert o.connections == conn_obj_


def test_fpu_05():
    conn_obj_ = {None: "dkjhfsjdh"}
    with pytest.raises(NoHostError) as exc_info:
        o = FabricPasswordUtility(
            connection_obj=conn_obj_,
            username="andrej",
            password="secret",
            ssh=True
        )
    assert str(exc_info.value).startswith("Specify host names")


def test_fpu_06():
    with pytest.raises(NoPasswordError) as exc_info:
        o = FabricPasswordUtility(
            connection_obj=conn_obj,
            username="andrej",
            password="secret",
            ssh=True
        )
    assert str(exc_info.value).startswith("Provide password")


def test_fpu_07():
    conn_obj_ = {
        "skvele.sk": 'jeez',
        "127.0.0.1": 'bujaka',
        "0.0.0.0": "fds%^&jkn",
    }
    o = FabricPasswordUtility(
        connection_obj=conn_obj_,
        username="andrej",
        password="secret",
        pwd_len=30
    )
    new_pwds = o.new_connection_map()
    for pwd in new_pwds.values():
        assert len(pwd) == o.pwd_len


def test_fpu_08():
    conn_obj_ = {
        "skvele.sk": 'jeez',
        "127.0.0.1": 'bujaka',
        "0.0.0.0": "fds%^&jkn",
    }
    o = FabricPasswordUtility(
        connection_obj=conn_obj_,
        username="andrej",
        password="secret",
        pwd_len=30
    )
    env_hosts = o.get_env_hosts_for_fabric()
    for i in env_hosts:
        assert i in conn_obj_

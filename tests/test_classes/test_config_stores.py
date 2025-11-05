# SPDX-License-Identifier: MIT
import pytest

from augur.application.config import JsonConfig, DatabaseConfig, NotWriteableException


def test_jsonconfig_readonly_flags():
    cfg = JsonConfig({"A": {"x": 1}})
    assert cfg.writable is False
    assert cfg.empty is False


def test_jsonconfig_empty_true_false():
    assert JsonConfig({}).empty is True
    assert JsonConfig({"A": {}}).empty is False


def test_jsonconfig_retrieve_has_get():
    data = {"Alpha": {"a": 1, "b": "str"}, "Beta": {}}
    cfg = JsonConfig(data)

    # retrieve full dict
    assert cfg.retrieve_dict() is data

    # has/get section
    assert cfg.has_section("Alpha") is True
    assert cfg.has_section("Missing") is False
    assert cfg.get_section("Alpha") == {"a": 1, "b": "str"}
    assert cfg.get_section("Missing") is None

    # has/get value
    assert cfg.has_value("Alpha", "a") is True
    assert cfg.has_value("Alpha", "missing") is False
    assert cfg.has_value("Missing", "a") is False
    assert cfg.get_value("Alpha", "a") == 1
    assert cfg.get_value("Alpha", "missing") is None
    assert cfg.get_value("Missing", "a") is None


@pytest.mark.parametrize(
    "callable_name, args, kwargs",
    [
        ("load_dict", ({"X": {"y": 2}},), {"ignore_existing": False}),
        ("clear", tuple(), {}),
        ("remove_section", ("X",), {}),
        ("create_section", ("X", {"y": 2}), {"ignore_existing": False}),
        ("remove_value", ("X", "y"), {}),
        ("add_value", ("X", "y", 2), {"ignore_existing": False}),
    ],
)
def test_jsonconfig_mutations_raise_not_writable(callable_name, args, kwargs):
    cfg = JsonConfig({"A": {"x": 1}})
    with pytest.raises(NotWriteableException):
        getattr(cfg, callable_name)(*args, **kwargs)

import pytest
import augur.application
import sqlalchemy as s
import json

def test_init_augur_regular():
    augur_app = augur.application.Application()
    assert augur_app is not None

# def test_discover_config_file(monkeypatch):
#     def mock_discover_config_file(augur_app):
#         return None
#     monkeypatch.setattr(augur.application.Application, "_discover_config_file", mock_discover_config_file)

#     augur_app = augur.application.Application()

#     assert augur_app._using_default_config is True

# def test_load_config_from_nonexistent_file(monkeypatch):
#     def mock_load_config_from_file(augur_app):
#         raise(FileNotFoundError())

#     monkeypatch.setattr(augur.application.Application, "_load_config_from_file", mock_load_config_from_file)

#     with pytest.raises(FileNotFoundError):
#         augur_app = augur.application.Application()
#         assert augur_app._using_default_config is True

# def test_load_config_from_invalid_json(monkeypatch):
#     def mock_load_config_from_file(augur_app):
#         raise(json.decoder.JSONDecodeError("fake", "error", 0))

#     monkeypatch.setattr(augur.application.Application, "_load_config_from_file", mock_load_config_from_file)

#     with pytest.raises(json.decoder.JSONDecodeError):
#         augur_app = augur.application.Application()
#         assert augur_app._using_default_config is True

def test_connect_to_database(monkeypatch):
    def mock_fail_connection(self):
        raise(s.exc.OperationalError("fake", "error", "message"))

    monkeypatch.setattr(s.engine.Engine, "connect", mock_fail_connection)
    monkeypatch.setenv("AUGUR_LOG_QUIET", "1")

    with pytest.raises(s.exc.OperationalError):
        augur_app = augur.application.Application()

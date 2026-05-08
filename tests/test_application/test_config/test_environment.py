from collectoss.application.environment import SystemEnv, _deprefix
import logging

logger = logging.getLogger(__name__)

prefixes = ["COLLECTOSS", "OTHER"]

def test_env_deprefix():
    assert _deprefix("OTHER_DB", prefixes) == "DB"
    assert _deprefix("COLLECTOSS_DB", prefixes) == "DB"

def test_env_deprefix_default():
    assert _deprefix("SOME_DB", prefixes) == "SOME_DB"
    assert _deprefix("THINGY_DB", prefixes) == "THINGY_DB"

def test_env_deprefix_unprefixed():
    assert _deprefix("DB", prefixes) == "DB"

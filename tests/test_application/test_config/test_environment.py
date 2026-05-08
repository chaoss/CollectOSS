from collectoss.application.environment import SystemEnv, extract_prefix
import logging

logger = logging.getLogger(__name__)

prefixes = ["COLLECTOSS", "OTHER"]

def test_env_extract_prefix():
    assert extract_prefix("OTHER_DB", prefixes) == "OTHER_"
    assert extract_prefix("COLLECTOSS_DB", prefixes) == "COLLECTOSS_"

def test_env_extract_prefix_default():
    assert extract_prefix("SOME_DB", prefixes) is None
    assert extract_prefix("THINGY_DB", prefixes) is None


def test_env_extract_prefix_unprefixed():
    assert extract_prefix("DB", prefixes) is None

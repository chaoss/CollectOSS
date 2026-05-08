from collectoss.application.environment import SystemEnv, extract_prefix
import logging
import os

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

def test_fetching_env():
    # plain
    os.environ["COLLECTOSS_NAME"] = "A"
    assert SystemEnv.get("COLLECTOSS_NAME") == "A"

    # fallback handling
    os.environ["OTHER_THING"] = "B"
    assert SystemEnv.get("COLLECTOSS_THING", None, prefixes) == "B"

    # cleanup
    del os.environ["COLLECTOSS_NAME"]
    del os.environ["OTHER_THING"]

def test_fetching_env_no_value():
    assert SystemEnv.get("COLLECTOSS_MISSING", None, prefixes) is None

def test_fetching_env_default():
    assert SystemEnv.get("COLLECTOSS_DEFAULT", "SOME", prefixes) == "SOME"

def test_no_known_prefix():
    # fallback handling
    os.environ["THING"] = "C"
    assert SystemEnv.get("THING", None, prefixes) == "C"


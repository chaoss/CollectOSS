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

def test_fetching_env_backwards():
    os.environ["COLLECTOSS_NAME"] = "A"
    assert SystemEnv.get("OTHER_NAME", None, prefixes) == "A"

    # cleanup
    del os.environ["COLLECTOSS_NAME"]

def test_fetching_env_no_value():
    assert SystemEnv.get("COLLECTOSS_MISSING", None, prefixes) is None

def test_fetching_env_default():
    assert SystemEnv.get("COLLECTOSS_DEFAULT", "SOME", prefixes) == "SOME"

def test_no_known_prefix():
    # fallback handling
    os.environ["THING"] = "C"
    assert SystemEnv.get("THING", None, prefixes) == "C"


def test_get_bool_trues():

    cases = ["1", "true", "True", "TRUE", "y", "Y", "yes", "Yes"]

    for case in cases:
        os.environ["OTHER_BOOL"] = case
        assert SystemEnv.get_bool("OTHER_BOOL", False, prefixes) == True
        del os.environ["OTHER_BOOL"]

def test_get_bool_falses():

    cases = ["0", "false", "False", "FALSE", "n", "N", "no", "No"]

    for case in cases:
        os.environ["OTHER_BOOL"] = case
        assert SystemEnv.get_bool("OTHER_BOOL", True, prefixes) == False
        del os.environ["OTHER_BOOL"]

def test_get_bool_default():

    cases = ["?", "maybe", "Stuff", "333"]

    for case in cases:
        os.environ["OTHER_BOOL"] = case
        assert SystemEnv.get_bool("OTHER_BOOL", False, prefixes) == False
        del os.environ["OTHER_BOOL"]

    

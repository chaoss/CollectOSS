import pytest

from collectoss.util.keys import mask_key


def test_none():
    assert mask_key(None) is None

def test_empty_string():
    assert mask_key("") == "*" * 6 + " Type: empty string"

def test_non_string():
    result = mask_key(12345)
    assert "*" in result
    assert str(type(12345)) in result


def test_non_string_list():
    result = mask_key([1, 2, 3])
    assert "*" in result
    assert str(type([])) in result


def test_short_string():
    assert mask_key("short") == f"******"


def test_long_string_masked_correctly():
    key = "ghp_abcdefghij"  # 14 chars → first 6 + 6 stars + last 3
    assert mask_key(key) == "ghp_ab******hij"


def test_exactly_one_over_boundary():
    # 10 chars: first 6 + 6 stars + last 3
    key = "1234567890"
    assert mask_key(key) == "123456******890"


def test_default_star_count_is_six():
    key = "abcdefghijk"  # 11 chars
    result = mask_key(key)
    middle = result[6:-3]
    assert middle == "******"


def test_custom_first_last_stars():
    # first=2, last=2, stars=3 → boundary=4; "hello" is 5 chars → masked
    assert mask_key("hello", first=2, last=2, stars=3) == "he***lo"


def test_custom_stars_count_in_output():
    key = "abcdefghijk"
    result = mask_key(key, stars=10)
    assert result == "abcdef**********ijk"



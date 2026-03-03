import pytest
import uuid
from augur.tasks.util.AugurUUID import AugurUUID, GithubUUID, GitlabUUID, UnresolvableUUID

# AugurUUID tests

# this checks whether a brand new AugurUUID object starts as 16 zero bytes
def test_augur_uuid_initializes_with_16_zero_bytes():
    uid = AugurUUID()
    assert len(uid.bytes) == 16
    assert all(b == 0 for b in uid.bytes)

# checks that githubUUID sets its platform number to 1
def test_github_uuid_platform_is_1():
    uid = GithubUUID()
    assert uid["platform"] == 1

# checks that gitlabUUID sets its platform number to 2
def test_gitlab_uuid_platform_is_2():
    uid = GitlabUUID()
    assert uid["platform"] == 2

def test_unresolvable_uuid_platform_is_0():
    uid = UnresolvableUUID()
    assert uid["platform"] == 0

# checks the that you can store a value in the user field
def test_github_uuid_set_user():
    uid = GithubUUID()
    uid["user"] = 12345
    assert uid["user"] == 12345

# checks the that you can store a value in the user field
def test_gitlab_uuid_set_user():
    uid = GitlabUUID()
    uid["user"] = 99999
    assert uid["user"] == 99999

# checks that to_UUID returs the uuid.UUID object
def test_to_uuid_returns_valid_uuid():
    uid = GithubUUID()
    uid["user"] = 15
    result = uid.to_UUID()
    assert isinstance(result, uuid.UUID)

# checks that set_byte correctly rejects a value that is too large
def test_set_byte_raises_on_invalid_value():
    uid = AugurUUID()
    with pytest.raises(ValueError):
        uid.set_byte(0, 256)  # too big for one byte

# checks that set_byte rejects an index that doesnt exist
def test_set_byte_raises_on_out_of_range_index():
    uid = AugurUUID()
    with pytest.raises(IndexError):
        uid.set_byte(16, 1)  # index 16 is out of bounds

# checks that 2 UUIDs with the same values are considered equal.
def test_equality():
    uid1 = GithubUUID()
    uid2 = GithubUUID()
    uid1["user"] = 100
    uid2["user"] = 100
    assert uid1 == uid2

# checks that 2 UUIDs with different values are not equal
def test_inequality():
    uid1 = GithubUUID()
    uid2 = GithubUUID()
    uid1["user"] = 100
    uid2["user"] = 200
    assert uid1 != uid2

# checks that writeint correctly rejects a number
def test_write_int_raises_on_overflow():
    uid = GithubUUID()
    with pytest.raises(ValueError):
        uid["user"] = 99999999999  # too big for 4 bytes

# checks that the same user produces different user IDs across platforms
def test_github_and_gitlab_different_for_same_user():
    github_uid = GithubUUID()
    gitlab_uid = GitlabUUID()
    github_uid["user"] = 100
    gitlab_uid["user"] = 100
    assert github_uid != gitlab_uid
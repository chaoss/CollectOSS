import pytest
import uuid
from collectoss.tasks.util.ContributorUUID import ContributorUUID, GithubUUID, GitlabUUID, UnresolvableUUID

# ContributorUUID tests
@pytest.mark.unit
class TestContributorUUID:
    # this checks whether a brand new ContributorUUID object starts as 16 zero bytes
    def test_augur_uuid_initializes_with_16_zero_bytes(self):
        uid = ContributorUUID()
        assert len(uid.bytes) == 16
        assert all(b == 0 for b in uid.bytes)

    # checks that githubUUID sets its platform number to 1
    def test_github_uuid_platform_is_1(self):
        uid = GithubUUID()
        assert uid["platform"] == 1

    # checks that gitlabUUID sets its platform number to 2
    def test_gitlab_uuid_platform_is_2(self):
        uid = GitlabUUID()
        assert uid["platform"] == 2

    # checks the that you can store a value in the user field
    def test_github_uuid_set_user(self):
        uid = GithubUUID()
        uid["user"] = 12345
        assert uid["user"] == 12345

    # tests platform_id edge cases
    def test_set_platform_id_raises_on_non_integer(self):
        uid = ContributorUUID()
        with pytest.raises(ValueError):
            uid.set_platform_id("github")

    def test_set_platform_id_raises_on_overflow(self):
        uid = ContributorUUID()
        with pytest.raises(ValueError):
            uid.set_platform_id(256)  # too big for 1 byte

    # checks that writing to one field doesnt accidentally overwrite bytes belonging to another field
    def test_fields_dont_overlap(self):
        uid = GithubUUID()

        uid["user"] = 12345
        uid["repo"] = 99999

        assert uid["user"] == 12345
        assert uid["repo"] == 99999

    # checks that to_UUID returs the uuid.UUID object
    def test_to_uuid_returns_valid_uuid(self):
        uid = GithubUUID()
        uid["user"] = 15
        result = uid.to_UUID()
        assert isinstance(result, uuid.UUID)

    # checks the start_byte is within range(0, 16) for set_bytes
    def test_set_bytes_raises_on_invalid_start_byte(self):
        uid = ContributorUUID()
        with pytest.raises(ValueError):
            uid.set_bytes([1, 2, 3], 16)

    # checks that set_bytes correctly raises an error when you write more bytes that will fit in the UUID starting at a given position
    def test_set_bytes_raises_on_too_many_bytes(self):
        uid = ContributorUUID()
        with pytest.raises(ValueError):
            uid.set_bytes([1] * 10, 10)

    # checks that writeint correctly rejects a number
    def test_write_int_raises_on_overflow(self):
        uid = GithubUUID()
        with pytest.raises(ValueError):
            uid["user"] = 99999999999  # too big for 4 bytes

    def test_write_int_with_non_integer(self):
        uid = GithubUUID()

        with pytest.raises(ValueError):
            uid.write_int("abc", 1, 4)

    def test_write_int_and_get_int_roundtrip(self):
        uid = ContributorUUID()
        uid.write_int(65535, 1, 2)
        assert uid.get_int(1, 2) == 65535

    # checks __int__ method
    def test_int_conversion(self):
        uid = ContributorUUID()
        uid.set_byte(15, 1)
        assert int(uid) == 1

    def test_get_byte_invalid_index(self):
        uid = ContributorUUID()
        with pytest.raises(IndexError):
            uid.get_byte(20)

    # checks that set_byte correctly rejects a value that is too large
    def test_set_byte_raises_on_invalid_value(self):
        uid = ContributorUUID()
        with pytest.raises(ValueError):
            uid.set_byte(0, 256)  # too big for one byte

    # checks that set_byte rejects an index that doesnt exist
    def test_set_byte_raises_on_out_of_range_index(self):
        uid = ContributorUUID()
        with pytest.raises(IndexError):
            uid.set_byte(16, 1)  # index 16 is out of bounds

    def test_set_byte_raises_on_non_integer(self):
        uid = ContributorUUID()
        with pytest.raises(ValueError):
            uid.set_byte(0, "hello")

    # checks that 2 UUIDs with the same values are considered equal.
    def test_equality(self):
        uid1 = GithubUUID()
        uid2 = GithubUUID()
        uid1["user"] = 100
        uid2["user"] = 100
        assert uid1 == uid2

    # checks that 2 UUIDs with different values are not equal
    def test_inequality(self):
        uid1 = GithubUUID()
        uid2 = GithubUUID()
        uid1["user"] = 100
        uid2["user"] = 200
        assert uid1 != uid2

    # checks that the same user produces different user IDs across platforms
    def test_github_and_gitlab_different_for_same_user(self):
        github_uid = GithubUUID()
        gitlab_uid = GitlabUUID()
        github_uid["user"] = 100
        gitlab_uid["user"] = 100
        assert github_uid != gitlab_uid

    def test_dict_representation(self):
        uid = GithubUUID()
        uid["user"] = 10

        result = uid.__dict__()

        assert result["platform"] == 1
        assert result["user"] == 10

    def test_string_representation(self):
        uid = GithubUUID()
        uid["user"] = 10

        result = str(uid)

        assert "user" in result
        assert "platform" in result

    def test_setting_same_field_twice(self):
        uid = GithubUUID()
        uid["user"] = 42
        uid["user"] = 100  # overwrite with different value
        assert uid["user"] == 100
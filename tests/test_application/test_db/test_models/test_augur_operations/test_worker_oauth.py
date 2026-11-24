import datetime
from datetime import timezone, timedelta
import sqlalchemy as sa

from collectoss.application.db.models import WorkerOauth


def test_worker_oauth_model_schema_attributes():
    """Verify WorkerOauth table definition, schema, and column attributes."""
    table = WorkerOauth.__table__
    assert table.name == "worker_oauth"
    assert table.schema == "operations"

    # Verify last_rotated column is nullable (so existing keys are not backfilled with current date)
    assert "last_rotated" in table.c
    last_rotated_col = table.c.last_rotated
    assert isinstance(last_rotated_col.type, sa.DateTime)
    assert last_rotated_col.type.timezone is True
    assert last_rotated_col.nullable is True
    assert last_rotated_col.comment == "Timestamp when the API key was last rotated or added, or NULL if not yet rotated"
    assert last_rotated_col.server_default is None

    # Verify expiry_date column
    assert "expiry_date" in table.c
    expiry_col = table.c.expiry_date
    assert isinstance(expiry_col.type, sa.DateTime)
    assert expiry_col.type.timezone is True
    assert expiry_col.nullable is True
    assert expiry_col.comment == "Timestamp when the API key expires, or NULL if no expiration"


def test_worker_oauth_instantiation_defaults():
    """Verify default values upon model instantiation."""
    record = WorkerOauth(
        name="test_key",
        consumer_key="ckey",
        consumer_secret="csec",
        access_token="ghp_testtoken",
        access_token_secret="atsec",
        platform="github",
    )
    assert record.name == "test_key"
    assert record.access_token == "ghp_testtoken"
    assert record.expiry_date is None
    assert record.is_expired is False


def test_worker_oauth_explicit_rotation_and_expiry():
    """Verify explicit values for last_rotated and expiry_date."""
    now_utc = datetime.datetime.now(timezone.utc)
    future_utc = now_utc + timedelta(days=60)
    record = WorkerOauth(
        name="full_key",
        consumer_key="ckey",
        consumer_secret="csec",
        access_token="ghp_fulltoken",
        access_token_secret="atsec",
        platform="gitlab",
        last_rotated=now_utc,
        expiry_date=future_utc,
    )
    assert record.last_rotated == now_utc
    assert record.expiry_date == future_utc
    assert record.is_expired is False


def test_worker_oauth_is_expired_none():
    """Keys with no expiry_date should never be expired."""
    record = WorkerOauth(
        name="no_expiry_key",
        consumer_key="ckey",
        consumer_secret="csec",
        access_token="ghp_testtoken",
        access_token_secret="atsec",
        expiry_date=None,
    )
    assert record.is_expired is False


def test_worker_oauth_is_expired_future_utc():
    """Keys with a future UTC expiry_date should not be expired."""
    future_time = datetime.datetime.now(timezone.utc) + timedelta(days=30)
    record = WorkerOauth(
        name="future_key",
        consumer_key="ckey",
        consumer_secret="csec",
        access_token="ghp_testtoken",
        access_token_secret="atsec",
        expiry_date=future_time,
    )
    assert record.is_expired is False


def test_worker_oauth_is_expired_past_utc():
    """Keys with a past UTC expiry_date should be expired."""
    past_time = datetime.datetime.now(timezone.utc) - timedelta(days=1)
    record = WorkerOauth(
        name="expired_key",
        consumer_key="ckey",
        consumer_secret="csec",
        access_token="ghp_testtoken",
        access_token_secret="atsec",
        expiry_date=past_time,
    )
    assert record.is_expired is True


def test_worker_oauth_is_expired_with_timezone_offset():
    """Keys with non-UTC timezone offsets should evaluate accurately."""
    tz_ist = timezone(timedelta(hours=5, minutes=30))
    future_time = datetime.datetime.now(tz_ist) + timedelta(hours=10)
    past_time = datetime.datetime.now(tz_ist) - timedelta(hours=10)

    future_record = WorkerOauth(
        name="future_key_ist",
        consumer_key="ckey",
        consumer_secret="csec",
        access_token="ghp_testtoken",
        access_token_secret="atsec",
        expiry_date=future_time,
    )
    past_record = WorkerOauth(
        name="past_key_ist",
        consumer_key="ckey",
        consumer_secret="csec",
        access_token="ghp_testtoken",
        access_token_secret="atsec",
        expiry_date=past_time,
    )

    assert future_record.is_expired is False
    assert past_record.is_expired is True


def test_worker_oauth_is_expired_naive_datetime():
    """Naive datetimes should be compared cleanly without raising TypeError."""
    future_naive = datetime.datetime.now() + timedelta(days=10)
    past_naive = datetime.datetime.now() - timedelta(days=10)

    future_record = WorkerOauth(
        name="future_naive",
        consumer_key="ckey",
        consumer_secret="csec",
        access_token="tok",
        access_token_secret="sec",
        expiry_date=future_naive,
    )
    past_record = WorkerOauth(
        name="past_naive",
        consumer_key="ckey",
        consumer_secret="csec",
        access_token="tok",
        access_token_secret="sec",
        expiry_date=past_naive,
    )

    assert future_record.is_expired is False
    assert past_record.is_expired is True

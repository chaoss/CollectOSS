# SPDX-License-Identifier: MIT
"""Unit and integration tests for database fixtures and schema isolation."""
import importlib.util
from pathlib import Path

import pytest
import sqlalchemy as s

# Load root conftest explicitly to avoid conflict with nested conftest modules
_root_conftest_path = Path(__file__).resolve().parents[2] / "conftest.py"
_spec = importlib.util.spec_from_file_location("root_conftest", _root_conftest_path)
_root_conftest = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_root_conftest)

get_test_db_url = _root_conftest.get_test_db_url
pytest_collection_modifyitems = _root_conftest.pytest_collection_modifyitems


# ---------------------------------------------------------------------------
# Unit tests: Verification of config discovery, markers, and skipping logic
# ---------------------------------------------------------------------------

def test_get_test_db_url_resolution(monkeypatch):
    """Test resolution of the test database URL from the COLLECTOSS_TEST_DB variable."""
    for var in ("COLLECTOSS_TEST_DB",):
        monkeypatch.delenv(var, raising=False)

    # When none set, should return None
    assert get_test_db_url() is None

    # COLLECTOSS_TEST_DB set
    monkeypatch.setenv("COLLECTOSS_TEST_DB", "postgresql+psycopg2://user:pass@localhost:5432/test_compose_db")
    assert get_test_db_url() == "postgresql+psycopg2://user:pass@localhost:5432/test_compose_db"


def test_pytest_collection_skips_when_no_db(monkeypatch):
    """Verify that tests requiring database fixtures are automatically skipped when no DB URL is set."""
    for var in ("COLLECTOSS_TEST_DB",):
        monkeypatch.delenv(var, raising=False)

    class DummyConfig:
        def getoption(self, name, default=None):
            return None

    class DummyItem:
        def __init__(self, name, fixturenames=None, markers=None):
            self.name = name
            self.fixturenames = fixturenames or []
            self.markers = markers or []

        def get_closest_marker(self, marker_name):
            for m in self.markers:
                if getattr(m, "name", None) == marker_name or m == marker_name:
                    return m
            return None

        def add_marker(self, marker):
            self.markers.append(marker)

    # Item with db fixture
    item_with_fixture = DummyItem("test_db_op", fixturenames=["blank_db_schema"])
    # Item with explicit marker
    item_with_marker = DummyItem("test_db_marked", markers=[pytest.mark.database])
    # Pure unit test
    unit_item = DummyItem("test_pure_unit", fixturenames=["tmp_path"])

    items = [item_with_fixture, item_with_marker, unit_item]
    pytest_collection_modifyitems(DummyConfig(), items)

    # Both db items should have db mark and skip marker
    assert any(getattr(m, "name", None) == "skip" for m in item_with_fixture.markers)
    assert any(getattr(m, "name", None) == "skip" for m in item_with_marker.markers)
    # Unit item should remain unmarked and unskipped
    assert not any(getattr(m, "name", None) == "skip" for m in unit_item.markers)


# ---------------------------------------------------------------------------
# Database-backed integration tests: Schema isolation, session & lifecycle
# ---------------------------------------------------------------------------

@pytest.mark.database
def test_blank_db_schema_isolation(database_engine, blank_db_schema):
    """Verify that blank_db_schema creates a unique schema and isolates tables."""
    assert blank_db_schema.startswith("test_schema_")

    with database_engine.connect() as conn:
        # Check that schema exists in information_schema
        result = conn.execute(
            s.text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :s"),
            {"s": blank_db_schema},
        ).scalar()
        assert result == blank_db_schema

        # Create a table inside the blank schema
        conn.execute(s.text(f'CREATE TABLE "{blank_db_schema}".test_items (id SERIAL PRIMARY KEY, name VARCHAR(50))'))
        conn.execute(
            s.text(f'INSERT INTO "{blank_db_schema}".test_items (name) VALUES (:n)'),
            {"n": "item_alpha"},
        )
        conn.commit()

        # Query back
        row = conn.execute(
            s.text(f'SELECT name FROM "{blank_db_schema}".test_items WHERE id = 1')
        ).scalar()
        assert row == "item_alpha"


@pytest.mark.database
def test_multi_schema_isolation_factory(database_engine, schema_factory):
    """Verify that schema_factory creates mutually isolated schemas without cross-contamination."""
    schema_1 = schema_factory("tenant_a")
    schema_2 = schema_factory("tenant_b")

    assert schema_1 != schema_2

    with database_engine.connect() as conn:
        # Create identical table names in each schema with different data
        conn.execute(s.text(f'CREATE TABLE "{schema_1}".sample (id INT, value TEXT)'))
        conn.execute(s.text(f'CREATE TABLE "{schema_2}".sample (id INT, value TEXT)'))

        conn.execute(s.text(f'INSERT INTO "{schema_1}".sample VALUES (1, \'from_schema_1\')'))
        conn.execute(s.text(f'INSERT INTO "{schema_2}".sample VALUES (1, \'from_schema_2\')'))
        conn.commit()

        val_1 = conn.execute(s.text(f'SELECT value FROM "{schema_1}".sample WHERE id = 1')).scalar()
        val_2 = conn.execute(s.text(f'SELECT value FROM "{schema_2}".sample WHERE id = 1')).scalar()

        assert val_1 == "from_schema_1"
        assert val_2 == "from_schema_2"


@pytest.mark.database
def test_schema_teardown(database_engine, schema_factory):
    """Verify that schemas created via schema_factory are dropped after the test.

    Uses a second schema created outside the factory to prove the teardown is
    selective: tracked schemas are dropped, others are left alone.
    """
    schema = schema_factory("teardown_check")
    manual_schema = "teardown_manual_" + schema.rsplit("_", 1)[1]

    with database_engine.connect() as conn:
        conn.execute(s.text(f'CREATE SCHEMA "{manual_schema}"'))
        conn.commit()

    # Stash the names for post-teardown verification
    test_schema_teardown.tracked = schema
    test_schema_teardown.manual = manual_schema


@pytest.mark.database
def test_schema_teardown_verification(database_engine):
    """Runs after test_schema_teardown: its schemas must be gone except the manual one."""
    tracked = getattr(test_schema_teardown, "tracked", None)
    manual = getattr(test_schema_teardown, "manual", None)
    assert tracked and manual, "test_schema_teardown must run first (pytest runs file order by default)"

    with database_engine.connect() as conn:
        result = conn.execute(
            s.text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :s"),
            {"s": tracked},
        ).scalar()
        assert result is None, f"tracked schema {tracked} was not dropped on teardown"

        result = conn.execute(
            s.text("SELECT schema_name FROM information_schema.schemata WHERE schema_name = :s"),
            {"s": manual},
        ).scalar()
        assert result == manual, "untracked schema should not have been dropped"

        # Clean up the manually created schema
        conn.execute(s.text(f'DROP SCHEMA IF EXISTS "{manual}" CASCADE'))
        conn.commit()


@pytest.mark.database
def test_db_session_fixture(db_session, blank_db_schema):
    """Verify that db_session operates within the blank schema and handles commits and rollbacks."""
    db_session.execute(
        s.text('CREATE TABLE sample_entries (id SERIAL PRIMARY KEY, content VARCHAR(100))')
    )
    db_session.commit()

    db_session.execute(
        s.text('INSERT INTO sample_entries (content) VALUES (:c)'),
        {"c": "test_content"},
    )
    db_session.commit()

    result = db_session.execute(s.text('SELECT content FROM sample_entries')).scalar()
    assert result == "test_content"


@pytest.mark.database
def test_collectoss_db_session(collectoss_db_session, blank_db_schema):
    """Verify that CollectOSS DatabaseSession wrapper executes queries in the isolated schema."""
    collectoss_db_session.execute_sql(
        s.text('CREATE TABLE session_test (id INT PRIMARY KEY, title VARCHAR(50))')
    )
    collectoss_db_session.execute_sql(
        s.text('INSERT INTO session_test (id, title) VALUES (1, \'test_title\')')
    )

    rows = collectoss_db_session.execute_sql(
        s.text('SELECT title FROM session_test WHERE id = 1')
    ).fetchall()
    assert len(rows) == 1
    assert rows[0][0] == "test_title"

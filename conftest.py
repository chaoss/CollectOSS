#SPDX-License-Identifier: MIT
import os
import pytest
import re

import sqlalchemy as s
from sqlalchemy import text


from collectoss.application.db.models.base import Base
from collectoss.application.db.models import *  # ensure all models are imported/registered

default_repo_id = "25430"
default_repo_group_id = "10"

def get_test_db_url():
    """Resolve the database connection URL for schema-isolated tests.

    Precedence order:
    1. COLLECTOSS_TEST_DB environment variable

    Returns None if no database configuration is available.
    """

    for env_var in ("COLLECTOSS_TEST_DB"):
        val = os.environ.get(env_var)
        if val:
            return val

    return None

SCHEMAS = ["data", "operations", "spdx"]


@pytest.fixture(scope="session")
def database_engine():
    """Session-scoped SQLAlchemy engine connected to the test database.

    Verifies server connectivity; skips gracefully if the database server
    is unreachable or credentials fail.
    """
    url = get_test_db_url()
    if not url:
        pytest.skip("No database URL provided (set COLLECTOSS_TEST_DB, TEST_DB_URL, or pass --db-url)")

    try:
        engine = s.create_engine(
            url,
            pool_pre_ping=True,
            connect_args={"application_name": "collectoss_test_suite"},
        )
        with engine.connect() as conn:
            conn.execute(s.text("SELECT 1"))
    except Exception as err:
        pytest.skip(f"Could not connect to test database: {err}")

    yield engine

    engine.dispose()


@pytest.fixture(scope="session")
def db_session(database_engine):
    """Session-scoped ORM session for read-heavy tests."""
    from collectoss.application.db.session import DatabaseSession
    import logging
    logger = logging.getLogger("tests.pg")
    session = DatabaseSession(logger, database_engine)
    try:
        yield session
    finally:
        session.close()

def create_full_routes(routes):
    full_routes = []
    for route in routes:
        route = re.sub("<default_repo_id>", default_repo_id, route)
        route = re.sub("<default_repo_group_id>", default_repo_group_id, route)
        route = "http://localhost:5000/api/unstable/" + route
        full_routes.append(route)
    return full_routes


@pytest.fixture(autouse=False)
def clean_schema_db(database_engine):
    """Per-test fixture that truncates all tables before and after the test.
    Use for integration tests that write data.
    """
    _truncate_all(database_engine)
    yield database_engine
    _truncate_all(database_engine)


def _truncate_all(engine):
    """Truncate all tables in the known schemas."""
    schema_list_sql = ", ".join([f"'{s}'" for s in SCHEMAS])
    truncate_script = f"""
    DO $$
    DECLARE truncate_cmd TEXT;
    BEGIN
        SELECT INTO truncate_cmd
            'TRUNCATE TABLE ' ||
            string_agg(quote_ident(schemaname) || '.' || quote_ident(tablename), ', ') ||
            ' RESTART IDENTITY CASCADE'
        FROM pg_tables
        WHERE schemaname IN ({schema_list_sql});
        IF truncate_cmd IS NOT NULL THEN
            EXECUTE truncate_cmd;
        END IF;
    END $$;
    """
    with engine.connect() as conn:
        conn.execute(text(truncate_script))
        conn.commit()




DB_FIXTURE_AUTOMARK_NAMES = {
    "database_engine",
}


def pytest_collection_modifyitems(config, items):
    """Skip database-backed tests automatically when no database URL is provided."""
    db_url = get_test_db_url()
    skip_no_db = pytest.mark.skip(
        reason="Skipping database test: no database connection configured (set COLLECTOSS_TEST_DB, TEST_DB_URL, or pass --db-url)"
    )

    for item in items:
        has_db_mark = item.get_closest_marker("database") is not None
        uses_db_fixture = bool(DB_FIXTURE_AUTOMARK_NAMES.intersection(getattr(item, "fixturenames", [])))

        if has_db_mark or uses_db_fixture:
            if not has_db_mark:
                item.add_marker(pytest.mark.db)
            if not db_url:
                item.add_marker(skip_no_db)



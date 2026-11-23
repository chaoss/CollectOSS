#SPDX-License-Identifier: MIT

# pylint: disable=W0621

import logging
import os
import pytest
import re
import uuid

import sqlalchemy as s
from sqlalchemy import text
from sqlalchemy.pool import NullPool

from collectoss.application.db.session import DatabaseSession

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

def create_full_routes(routes):
    full_routes = []
    for route in routes:
        route = re.sub("<default_repo_id>", default_repo_id, route)
        route = re.sub("<default_repo_group_id>", default_repo_group_id, route)
        route = "http://localhost:5000/api/unstable/" + route
        full_routes.append(route)
    return full_routes

logger = logging.getLogger(__name__)



DB_FIXTURE_AUTOMARK_NAMES = {
    "database_engine",
    "schema_factory",
    "blank_db_schema",
    "isolated_engine",
    "db_session",
    "blank_collectoss_db_schema",
    "isolated_collectoss_engine",
    "collectoss_db_session",
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


@pytest.fixture
def schema_factory(db_engine):
    """Factory fixture allowing tests to dynamically create one or more isolated schemas.

    All schemas created during the test are automatically dropped (CASCADE) on teardown.
    """
    schemas_created = []

    def _create_schema(prefix="test_schema", random_name=True) -> str:
        schema_name = f"{prefix}_{uuid.uuid4().hex[:12]}" if random_name else prefix
        with db_engine.connect() as conn:
            conn.execute(s.text(f'CREATE SCHEMA "{schema_name}"'))
            conn.commit()
        schemas_created.append(schema_name)
        return schema_name

    yield _create_schema

    with db_engine.connect() as conn:
        for schema in schemas_created:
            try:
                conn.execute(s.text(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE'))
                conn.commit()
            except Exception as err:
                logger.warning(f"Failed to drop test schema {schema}: {err}")


@pytest.fixture
def blank_db_schema(schema_factory) -> str:
    """Provides a fresh, isolated PostgreSQL schema name for a single test.

    The schema is created before the test and automatically dropped on teardown.
    """
    return schema_factory()



@pytest.fixture
def isolated_engine(db_engine, blank_db_schema):
    """SQLAlchemy Engine whose connections automatically set search_path to the isolated schema."""
    engine = s.create_engine(
        db_engine.url,
        poolclass=NullPool,
    )

    @s.event.listens_for(engine, "connect")
    def _set_search_path(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(f'SET search_path TO "{blank_db_schema}", public')
        cursor.close()

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(db_engine, blank_db_schema):
    """Yields an SQLAlchemy ORM Session bound to the test's isolated blank schema.

    Sets search_path to the isolated schema, rolls back any pending transactions,
    and closes cleanly on teardown.
    """
    from sqlalchemy.orm import sessionmaker

    connection = db_engine.connect()
    connection.execute(s.text(f'SET search_path TO "{blank_db_schema}", public'))
    connection.commit()

    Session = sessionmaker(bind=connection)
    session = Session()

    try:
        yield session
    finally:
        session.rollback()
        session.close()
        connection.close()

# ---------------------------------------------------------------------------
# CollectOSS-specific schema fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def blank_collectoss_db_schema(schema_factory):
    """Provides a fresh, isolated PostgreSQL schema that structurally matches a CollectOSS db.

    The schema is created before the test and automatically dropped on teardown.
    Returns a list of the schemas in the collectOSS set. should always return the same strings as `SCHEMAS` list above.
    """
    yield [schema_factory(schema, random_name=False) for schema in SCHEMAS]


@pytest.fixture
def isolated_collectoss_engine(database_engine, blank_collectoss_db_schema):
    """SQLAlchemy Engine whose connections automatically set search_path to the isolated schema."""
    engine = s.create_engine(
        database_engine.url,
        poolclass=NullPool,
    )

    @s.event.listens_for(engine, "connect")
    def _set_search_path(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute(f'SET search_path TO {",".join(blank_collectoss_db_schema)}, public')
        cursor.close()

    
    Base.metadata.create_all(engine)
    # TODO: create materialized view tables too if not covered by the above?

    yield engine

    engine.dispose()


@pytest.fixture
def collectoss_db_session(isolated_collectoss_engine):
    """Yields a CollectOSS DatabaseSession instance operating inside the isolated schema."""
    session = DatabaseSession(logger, engine=isolated_collectoss_engine)
    try:
        yield session
    finally:
        session.close()


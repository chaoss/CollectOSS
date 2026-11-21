# SPDX-License-Identifier: MIT
# pylint: disable=redefined-outer-name
import json
import logging
import os
import re
import uuid
from typing import Optional

import psycopg2
import pytest
import sqlalchemy as s
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.pool import NullPool, StaticPool

from collectoss.application.config import SystemConfig
from collectoss.application.db.engine import (
    create_database_engine,
    execute_sql_file,
    parse_database_string,
)
from collectoss.application.db.session import DatabaseSession

logger = logging.getLogger(__name__)

default_repo_id = "25430"
default_repo_group_id = "10"


def create_full_routes(routes):
    full_routes = []
    for route in routes:
        route = re.sub("<default_repo_id>", default_repo_id, route)
        route = re.sub("<default_repo_group_id>", default_repo_group_id, route)
        route = "http://localhost:5000/api/unstable/" + route
        full_routes.append(route)
    return full_routes


# ---------------------------------------------------------------------------
# Database URL resolution and pytest configuration hooks
# ---------------------------------------------------------------------------

def pytest_addoption(parser):
    """Register custom CLI options for database-backed test execution."""
    parser.addoption(
        "--db-url",
        action="store",
        default=None,
        help="Database URL for database-backed tests (e.g. postgresql+psycopg2://user:pass@localhost:5432/dbname)",
    )


def get_test_db_url(config=None) -> Optional[str]:
    """Resolve the database connection URL for testing.

    Precedence order:
    1. CLI option `--db-url` passed to pytest
    2. TEST_DB_URL environment variable
    3. COLLECTOSS_DB environment variable
    4. AUGUR_DB environment variable
    5. db.config.json in the current working directory

    Returns None if no database configuration is available.
    """
    if config is not None:
        try:
            cli_url = config.getoption("--db-url", default=None)
            if cli_url:
                return cli_url
        except (ValueError, AttributeError):
            pass

    for env_var in ("TEST_DB_URL", "COLLECTOSS_DB", "AUGUR_DB"):
        val = os.environ.get(env_var)
        if val:
            return val

    if os.path.exists("db.config.json"):
        try:
            with open("db.config.json", "r", encoding="utf-8") as f:
                cfg = json.load(f)
            return (
                f"postgresql+psycopg2://{cfg['user']}:{cfg['password']}@"
                f"{cfg['host']}:{cfg['port']}/{cfg['database_name']}"
            )
        except Exception:
            pass

    return None


DB_FIXTURE_NAMES = {
    "db_engine",
    "schema_factory",
    "blank_db_schema",
    "isolated_engine",
    "db_session",
    "collectoss_db_session",
    "empty_db_template",
    "empty_db",
    "read_only_db",
    "test_db_engine",
    "test_db_session",
    "test_db_config",
}


def pytest_collection_modifyitems(config, items):
    """Skip database-backed tests automatically when no database URL is provided."""
    db_url = get_test_db_url(config)
    skip_no_db = pytest.mark.skip(
        reason="Skipping database test: no database connection configured (set COLLECTOSS_DB, TEST_DB_URL, or pass --db-url)"
    )

    for item in items:
        has_db_mark = item.get_closest_marker("db") is not None
        uses_db_fixture = bool(DB_FIXTURE_NAMES.intersection(getattr(item, "fixturenames", [])))

        if has_db_mark or uses_db_fixture:
            if not has_db_mark:
                item.add_marker(pytest.mark.db)
            if not db_url:
                item.add_marker(skip_no_db)


# ---------------------------------------------------------------------------
# Modern, schema-isolated database fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def db_engine(request):
    """Session-scoped SQLAlchemy engine connected to the test database.

    Verifies server connectivity; skips gracefully if the database server
    is unreachable or credentials fail.
    """
    db_url = get_test_db_url(request.config)
    if not db_url:
        pytest.skip("No database URL provided (set COLLECTOSS_DB, TEST_DB_URL, or pass --db-url)")

    try:
        engine = s.create_engine(
            db_url,
            pool_pre_ping=True,
            connect_args={"application_name": "collectoss_test_suite"},
        )
        with engine.connect() as conn:
            conn.execute(s.text("SELECT 1"))
    except Exception as err:
        pytest.skip(f"Could not connect to test database: {err}")

    yield engine

    engine.dispose()


@pytest.fixture
def schema_factory(db_engine):
    """Factory fixture allowing tests to dynamically create one or more isolated schemas.

    All schemas created during the test are automatically dropped (CASCADE) on teardown.
    """
    schemas_created = []

    def _create_schema(prefix="test_schema") -> str:
        schema_name = f"{prefix}_{uuid.uuid4().hex[:12]}"
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


@pytest.fixture
def collectoss_db_session(isolated_engine):
    """Yields a CollectOSS DatabaseSession instance operating inside the isolated schema."""
    session = DatabaseSession(logger, engine=isolated_engine)
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Backwards-compatible legacy fixtures and helper functions
# ---------------------------------------------------------------------------

def create_connection(dbname="postgres"):
    """Creates a raw psycopg2 connection to the database."""
    db_string = get_test_db_url()
    if not db_string:
        raise RuntimeError("No database URL configured for test connection")
    user, password, host, port, _ = parse_database_string(db_string)
    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname=dbname,
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn, conn.cursor()


def create_database(conn, cursor, db_name, template=None):
    if template:
        cursor.execute(sql.SQL("CREATE DATABASE {} WITH TEMPLATE {};").format(sql.Identifier(db_name), sql.Identifier(template)))
    else:
        cursor.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(db_name)))
    conn.commit()


def drop_database(cursor, db_name):
    cursor.execute(sql.SQL("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{}';".format(db_name)))
    cursor.execute(sql.SQL("DROP DATABASE {};").format(sql.Identifier(db_name)))


def generate_db_from_template(template_name):
    db_string = get_test_db_url()
    if not db_string:
        raise RuntimeError("No database URL configured for test database generation")
    user, password, host, port, _ = parse_database_string(db_string)

    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    test_db_name = "test_db_" + uuid.uuid4().hex
    test_db_string = db_string[:db_string.rfind("/") + 1] + test_db_name

    create_database(conn, cursor, test_db_name, template_name)

    engine = create_database_engine(test_db_string, poolclass=StaticPool, connect_args={"application_name": "collectoss tests"})
    yield engine

    engine.dispose()
    drop_database(cursor, test_db_name)
    cursor.close()
    conn.close()


def generate_template_db(sql_file_path):
    db_string = get_test_db_url()
    if not db_string:
        raise RuntimeError("No database URL configured for template database generation")
    user, password, host, port, _ = parse_database_string(db_string)

    conn = psycopg2.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        dbname="postgres",
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    test_db_name = "test_db_template_" + uuid.uuid4().hex
    create_database(conn, cursor, test_db_name)

    execute_sql_file(sql_file_path, test_db_name, user, password, host, port)

    cursor.execute(sql.SQL("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{}';".format(test_db_name)))

    yield test_db_name

    drop_database(cursor, test_db_name)
    cursor.close()
    conn.close()


@pytest.fixture(scope="session")
def empty_db_template(db_engine):
    yield from generate_template_db("tests/entire_db.sql")


@pytest.fixture(scope="session")
def empty_db(db_engine, empty_db_template):
    yield from generate_db_from_template(empty_db_template)


@pytest.fixture(scope="session")
def read_only_db(empty_db):
    database_name = empty_db.url.database
    test_username = "testuser"
    test_password = "testpass"
    schemas = ["public", "data", "operations"]

    empty_db.execute(s.text(f"CREATE USER testuser WITH PASSWORD '{test_password}';"))
    empty_db.execute(s.text(f"GRANT CONNECT ON DATABASE {database_name} TO {test_username};"))
    for schema in schemas:
        empty_db.execute(s.text(f"GRANT USAGE ON SCHEMA {schema} TO {test_username};"))
        empty_db.execute(s.text(f"GRANT SELECT ON ALL TABLES IN SCHEMA {schema} TO {test_username};"))

    db_string = get_test_db_url()
    _, _, host, port, _ = parse_database_string(db_string)
    read_only_engine = s.create_engine(f"postgresql+psycopg2://{test_username}:{test_password}@{host}:{port}/{database_name}")

    yield read_only_engine

    read_only_engine.dispose()
    empty_db.execute(s.text(f"REVOKE CONNECT ON DATABASE {database_name} FROM {test_username};"))
    for schema in schemas:
        empty_db.execute(s.text(f"REVOKE USAGE ON SCHEMA {schema} FROM {test_username};"))
        empty_db.execute(s.text(f"REVOKE SELECT ON ALL TABLES IN SCHEMA {schema} FROM {test_username};"))
    empty_db.execute(s.text(f"DROP USER {test_username};"))


@pytest.fixture
def test_db_engine(db_engine):
    """Backwards-compatible alias for db_engine."""
    return db_engine


@pytest.fixture
def test_db_session(test_db_engine):
    """Backwards-compatible DatabaseSession fixture."""
    session = DatabaseSession(logger, engine=test_db_engine)
    yield session
    session.close()


@pytest.fixture
def test_db_config(test_db_session):
    """Backwards-compatible SystemConfig fixture."""
    return SystemConfig(logger, test_db_session)

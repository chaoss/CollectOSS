import logging
import uuid

import pytest
import psycopg2
import sqlalchemy as s
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from sqlalchemy.pool import StaticPool

from collectoss.application.db.engine import get_database_string, parse_database_string, create_database_engine
from collectoss.application.db.models.operations import ForgeInstance
from collectoss.application.db.session import DatabaseSession
from collectoss.util.enums import ForgePlatformType
from collectoss.util.startup import initialize_tables


logger = logging.getLogger(__name__)


@pytest.fixture(scope="module")
def forge_db_engine():
    """Create a temporary database containing only an empty operations.forge_instance table

    The forge_instance table is not in tests/entire_db.sql, so it is created
    from the SQLAlchemy model (the source of truth for the live schema).
    """

    db_string = get_database_string()
    user, password, host, port, _ = parse_database_string(db_string)

    # connect to the default postgres database to create/drop the test database
    conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname="postgres")
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()

    test_db_name = "test_startup_" + uuid.uuid4().hex
    cursor.execute(sql.SQL("CREATE DATABASE {};").format(sql.Identifier(test_db_name)))

    test_db_string = db_string[:db_string.rfind("/") + 1] + test_db_name
    engine = create_database_engine(test_db_string, poolclass=StaticPool, connect_args={"application_name": "collectoss tests"})

    with engine.begin() as connection:
        connection.execute(s.text("CREATE SCHEMA IF NOT EXISTS operations"))
    ForgeInstance.__table__.create(engine, checkfirst=True)

    yield engine

    engine.dispose()

    cursor.execute(sql.SQL("SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname='{}';".format(test_db_name)))
    cursor.execute(sql.SQL("DROP DATABASE {};").format(sql.Identifier(test_db_name)))
    cursor.close()
    conn.close()


@pytest.fixture(autouse=True)
def clear_forge_instances(forge_db_engine):
    """Ensure each test starts with an empty forge_instance table"""

    with DatabaseSession(logger, engine=forge_db_engine) as session:
        session.query(ForgeInstance).delete()
        session.commit()


def test_initialize_tables_populates_default_forges(forge_db_engine):

    initialize_tables(forge_db_engine, logger)

    with DatabaseSession(logger, engine=forge_db_engine) as session:

        instances = session.query(ForgeInstance).all()
        assert len(instances) == 2

        by_platform = {instance.platform_type: instance for instance in instances}
        assert set(by_platform.keys()) == {ForgePlatformType.GITHUB.value, ForgePlatformType.GITLAB.value}

        github = by_platform[ForgePlatformType.GITHUB.value]
        assert github.name == "GitHub (default)"
        assert github.domain_name == "github.com"
        assert github.enabled is True
        assert github.privacy_url == "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement"
        assert github.terms_url == "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service"
        assert github.policy_reviewed_by == "CollectOSS Maintainers"
        assert github.policy_reviewed_date is not None
        assert github.policy_review_comments

        gitlab = by_platform[ForgePlatformType.GITLAB.value]
        assert gitlab.name == "GitLab (default)"
        assert gitlab.domain_name == "gitlab.com"
        assert gitlab.enabled is True
        assert gitlab.privacy_url == "https://about.gitlab.com/privacy/"
        assert gitlab.terms_url == "https://about.gitlab.com/terms/"
        assert gitlab.policy_reviewed_by == "CollectOSS Maintainers"
        assert gitlab.policy_reviewed_date is not None
        assert gitlab.policy_review_comments


def test_initialize_tables_is_idempotent(forge_db_engine):

    initialize_tables(forge_db_engine, logger)
    initialize_tables(forge_db_engine, logger)

    with DatabaseSession(logger, engine=forge_db_engine) as session:
        assert session.query(ForgeInstance).count() == 2


def test_initialize_tables_skips_defaults_when_forges_exist(forge_db_engine):

    with DatabaseSession(logger, engine=forge_db_engine) as session:
        session.add(ForgeInstance(
            platform_type=ForgePlatformType.GITLAB.value,
            name="GitLab self-hosted",
            domain_name="gitlab.example.com",
            privacy_url="https://gitlab.example.com/privacy/",
            terms_url="https://gitlab.example.com/terms/",
            policy_reviewed_by="test",
            enabled=False
        ))
        session.commit()

    initialize_tables(forge_db_engine, logger)

    with DatabaseSession(logger, engine=forge_db_engine) as session:

        instances = session.query(ForgeInstance).all()
        assert len(instances) == 1

        # the pre-existing forge is untouched
        assert instances[0].domain_name == "gitlab.example.com"
        assert instances[0].name == "GitLab self-hosted"
        assert instances[0].enabled is False

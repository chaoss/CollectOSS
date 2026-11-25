import logging
import pytest

from collectoss.application.db.models.operations import ForgeInstance
from collectoss.application.db.session import DatabaseSession
from collectoss.util.enums import ForgePlatformType
from collectoss.util.startup import initialize_table_data

logger = logging.getLogger(__name__)


@pytest.mark.database
def test_initialize_table_data_populates_default_forges(isolated_collectoss_engine, collectoss_db_session):

    instances = collectoss_db_session.query(ForgeInstance).all()
    assert len(instances) == 0

    initialize_table_data(isolated_collectoss_engine, logger)

    instances = collectoss_db_session.query(ForgeInstance).all()
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


@pytest.mark.database
def test_initialize_table_data_is_idempotent(isolated_collectoss_engine, collectoss_db_session):

    assert collectoss_db_session.query(ForgeInstance).count() == 0

    initialize_table_data(isolated_collectoss_engine, logger)
    assert collectoss_db_session.query(ForgeInstance).count() == 2

    initialize_table_data(isolated_collectoss_engine, logger)
    assert collectoss_db_session.query(ForgeInstance).count() == 2


@pytest.mark.database
def test_initialize_table_data_skips_defaults_when_forges_exist(isolated_collectoss_engine, collectoss_db_session):

    collectoss_db_session.add(ForgeInstance(
        platform_type=ForgePlatformType.GITLAB.value,
        name="GitLab self-hosted",
        domain_name="gitlab.example.com",
        privacy_url="https://gitlab.example.com/privacy/",
        terms_url="https://gitlab.example.com/terms/",
        policy_reviewed_by="test",
        enabled=False
    ))
    collectoss_db_session.commit()

    initialize_table_data(isolated_collectoss_engine, logger)

    instances = collectoss_db_session.query(ForgeInstance).all()
    assert len(instances) == 1

    # the pre-existing forge is untouched
    assert instances[0].domain_name == "gitlab.example.com"
    assert instances[0].name == "GitLab self-hosted"
    assert instances[0].enabled is False

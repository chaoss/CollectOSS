"""Populate default data for forge_instances table

Revision ID: 47
Revises: 46
Create Date: 2026-11-16 12:19:48.031786

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy import Column, Integer, String, Boolean, DateTime, func
from sqlalchemy.orm import relationship, DeclarativeBase, Session

from enum import Enum
from datetime import datetime
from zoneinfo import ZoneInfo

# revision identifiers, used by Alembic.
revision = '47'
down_revision = '46'
branch_labels = None
depends_on = None

# Normally we dont allow migrations to create/modify data in a database except as part of structural schema changes
# however, we anticipate a future migration to adjust foreign keys to rely on this table instead, and need to
# effectively gaurantee the data exists prior to that migration existing in a way that is automatic for most instances.


# We include a copy of the forge_instance schema definition and other relevant types here because it may change in the future and we need to be accurate
# to what the state of a CollectOSS instance is going to be prior to this migration


class ForgePlatformType(Enum):
    """Identification values for different known forges.
    Intended for helping identify the relevant API endpoints and tasks to use for collection"""
    UNRESOLVEABLE = 0
    GITHUB = 1
    GITLAB = 2

class Base(DeclarativeBase):
    pass

class ForgeInstance(Base):
    __tablename__ = "forge_instance"
    __table_args__ = { "schema": "operations" }

    id = Column(Integer, primary_key=True, nullable=False, comment="Internal unique identifier for this forge instance")
    # platform_type stores an integer that CollectOSS maps/will map to it's internal platform identifier Enum 
    # (as used in ContributorUUID) for identifying the API endpoints and tasks to use for collection
    platform_type = Column(Integer, nullable=False, comment="Type specifier identifying the relevant platform API interface to CollectOSS")
    name = Column(String, nullable=False, comment="User-specified name for this forge instance")
    # https://stackoverflow.com/a/54800233
    date_added = Column(DateTime(timezone=True), nullable=False, default=func.now())
    domain_name = Column(String, nullable=False, comment="The base domain name (without the scheme) where this instance is hosted")
    enabled = Column(Boolean, default=True, nullable=False, comment="denotes whether collection should run for this instance")
    privacy_url = Column(String, nullable=False, comment="The link to the privacy policy for this instance")
    terms_url = Column(String, nullable=False, comment="The link to the terms of service for this instance")
    policy_reviewed_date = Column(DateTime(timezone=True), nullable=False, default=func.now())
    policy_reviewed_by = Column(String, nullable=False, comment="Who conducted the last review of these policies")
    policy_review_comments = Column(String, nullable=True, comment="Reviewer comments from the most recent policy review.")
    api_keys = relationship("WorkerOauth")

# these are the default definitions for forge instance objects in the DB provided by CollectOSS maintainers.
# Future instances will likely be added by instance operators, not via migrations
DEFAULT_FORGES = [
    ForgeInstance(
        platform_type=ForgePlatformType.GITHUB.value,
        name="GitHub (defualt)",
        domain_name="github.com",
        privacy_url = "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement",
        terms_url = "https://docs.github.com/en/site-policy/github-terms/github-terms-of-service",
        policy_reviewed_date = datetime(2026, 10, 12, tzinfo=ZoneInfo("America/New_York")),
        policy_reviewed_by = "CollectOSS Maintainers",
        policy_review_comments = "CollectOSS primarily accesses public information from GitHub. Terms state: "
            "\"Depending on your account settings, we may share Personal Data with other users of the Services "
            " and the public. You control what information is made public.\"",
        enabled=True
    ),
    ForgeInstance(
        platform_type=ForgePlatformType.GITLAB.value,
        name="GitLab (defualt)",
        domain_name="gitlab.com",
        privacy_url = "https://about.gitlab.com/privacy/",
        terms_url = "https://about.gitlab.com/terms/",
        policy_reviewed_date = datetime(2026, 11, 16, tzinfo=ZoneInfo("America/New_York")),
        policy_reviewed_by = "CollectOSS Maintainers",
        policy_review_comments = "CollectOSS primarily accesses public information from GitLab. Terms state: "
            "\"We may share your Personal Data with other users of the Services and with the public if you "
            "choose to make your SaaS Profile public. You have control over what information is public;\"",               
        enabled=True
    )
]

def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    session.add_all(DEFAULT_FORGES)
    session.flush()


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    # Delete only the rows you seeded (skip this if downgrade drops the whole table)
    forge_ids = [forge.id for forge in DEFAULT_FORGES]
    session.execute(sa.delete(ForgeInstance).where(ForgeInstance.id.in_(forge_ids)))
    session.flush()

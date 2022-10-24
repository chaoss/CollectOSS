# coding: utf-8
from sqlalchemy import BigInteger, SmallInteger, Column, Index, Integer, String, Table, text, UniqueConstraint, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP

from augur.application.db.models.base import Base

metadata = Base.metadata


t_all = Table(
    "all",
    metadata,
    Column("Name", String),
    Column("Bytes", String),
    Column("Lines", String),
    Column("Code", String),
    Column("Comment", String),
    Column("Blank", String),
    Column("Complexity", String),
    Column("Count", String),
    Column("WeightedComplexity", String),
    Column("Files", String),
    schema="augur_operations",
)


class AugurSetting(Base):
    __tablename__ = "augur_settings"
    __table_args__ = {
        "schema": "augur_operations",
        "comment": "Augur settings include the schema version, and the Augur API Key as of 10/25/2020. Future augur settings may be stored in this table, which has the basic structure of a name-value pair. ",
    }

    id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_operations.augur_settings_id_seq'::regclass)"
        ),
    )
    setting = Column(String)
    value = Column(String)
    last_modified = Column(TIMESTAMP(precision=0), server_default=text("CURRENT_DATE"))


t_repos_fetch_log = Table(
    "repos_fetch_log",
    metadata,
    Column("repos_id", Integer, nullable=False),
    Column("status", String(128), nullable=False),
    Column(
        "date",
        TIMESTAMP(precision=0),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("repos_id,statusops", "repos_id", "status"),
    schema="augur_operations",
    comment="For future use when we move all working tables to the augur_operations schema. ",
)

class WorkerHistory(Base):
    __tablename__ = "worker_history"
    __table_args__ = {
        "schema": "augur_operations",
        "comment": "This table stores the complete history of job execution, including success and failure. It is useful for troubleshooting. ",
    }

    history_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_operations.gh_worker_history_history_id_seq'::regclass)"
        ),
    )
    repo_id = Column(BigInteger)
    worker = Column(String(255), nullable=False)
    job_model = Column(String(255), nullable=False)
    oauth_id = Column(Integer)
    timestamp = Column(TIMESTAMP(precision=0), nullable=False)
    status = Column(String(7), nullable=False)
    total_results = Column(Integer)


class WorkerJob(Base):
    __tablename__ = "worker_job"
    __table_args__ = {
        "schema": "augur_operations",
        "comment": "This table stores the jobs workers collect data for. A job is found in the code, and in the augur.config.json under the construct of a “model”. ",
    }

    job_model = Column(String(255), primary_key=True)
    state = Column(Integer, nullable=False, server_default=text("0"))
    zombie_head = Column(Integer)
    since_id_str = Column(
        String(255), nullable=False, server_default=text("'0'::character varying")
    )
    description = Column(String(255), server_default=text("'None'::character varying"))
    last_count = Column(Integer)
    last_run = Column(
        TIMESTAMP(precision=0), server_default=text("NULL::timestamp without time zone")
    )
    analysis_state = Column(Integer, server_default=text("0"))
    oauth_id = Column(Integer, nullable=False)


class WorkerOauth(Base):
    __tablename__ = "worker_oauth"
    __table_args__ = {
        "schema": "augur_operations",
        "comment": "This table stores credentials for retrieving data from platform API’s. Entries in this table must comply with the terms of service for each platform. ",
    }

    oauth_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_operations.worker_oauth_oauth_id_seq'::regclass)"
        ),
    )
    name = Column(String(255), nullable=False)
    consumer_key = Column(String(255), nullable=False)
    consumer_secret = Column(String(255), nullable=False)
    access_token = Column(String(255), nullable=False)
    access_token_secret = Column(String(255), nullable=False)
    repo_directory = Column(String)
    platform = Column(String, server_default=text("'github'::character varying"))


class WorkerSettingsFacade(Base):
    __tablename__ = "worker_settings_facade"
    __table_args__ = {
        "schema": "augur_operations",
        "comment": "For future use when we move all working tables to the augur_operations schema. ",
    }

    id = Column(Integer, primary_key=True)
    setting = Column(String(32), nullable=False)
    value = Column(String, nullable=False)
    last_modified = Column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


t_working_commits = Table(
    "working_commits",
    metadata,
    Column("repos_id", Integer, nullable=False),
    Column(
        "working_commit", String(40), server_default=text("'NULL'::character varying")
    ),
    schema="augur_operations",
    comment="For future use when we move all working tables to the augur_operations schema. ",
)


class Config(Base):
    id = Column(SmallInteger, primary_key=True, nullable=False)
    section_name = Column(String, nullable=False)
    setting_name = Column(String, nullable=False)
    value = Column(String)
    type = Column(String)

    __tablename__ = 'config'
    __table_args__ = (
        UniqueConstraint('section_name', "setting_name", name='unique-config-setting'),
        {"schema": "augur_operations"}
    )

# add admit column to database
class User(Base):
    user_id = Column(Integer, primary_key=True)
    login_name = Column(String, nullable=False)
    login_hashword = Column(String, nullable=False)
    email = Column(String, nullable=False)
    text_phone = Column(String)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    admin = Column(Boolean, nullable=False)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP"))
    
    __tablename__ = 'users'
    __table_args__ = (
        UniqueConstraint('email', name='user-unique-email'),
        UniqueConstraint('login_name', name='user-unique-name'),
        UniqueConstraint('text_phone', name='user-unique-phone'),
        {"schema": "augur_operations"}
    )



class UserRepo(Base):
    __tablename__ = "user_repos"
    __table_args__ = (
        {
            "schema": "augur_operations"
        }
    )

    user_id = Column(
        ForeignKey("augur_operations.users.user_id"), primary_key=True, nullable=False
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id"), primary_key=True, nullable=False
    )


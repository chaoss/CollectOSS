# coding: utf-8
from sqlalchemy import (
    BigInteger,
    Boolean,
    CHAR,
    Column,
    Date,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    SmallInteger,
    String,
    Table,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, TIMESTAMP, UUID
from sqlalchemy.orm import relationship
from augur_db.models.base import Base

metadata = Base.metadata


t_analysis_log = Table(
    "analysis_log",
    metadata,
    Column("repos_id", Integer, nullable=False),
    Column("status", String, nullable=False),
    Column(
        "date_attempted",
        TIMESTAMP(precision=0),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    schema="augur_data",
)
Index('repos_id', t_analysis_log.c.repos_id)



class ChaossMetricStatus(Base):
    __tablename__ = "chaoss_metric_status"
    __table_args__ = {
        "schema": "augur_data",
        "comment": "This table used to track CHAOSS Metric implementations in Augur, but due to the constantly changing location of that information, it is for the moment not actively populated. ",
    }

    cms_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.chaoss_metric_status_cms_id_seq'::regclass)"
        ),
    )
    cm_group = Column(String)
    cm_source = Column(String)
    cm_type = Column(String)
    cm_backend_status = Column(String)
    cm_frontend_status = Column(String)
    cm_defined = Column(Boolean)
    cm_api_endpoint_repo = Column(String)
    cm_api_endpoint_rg = Column(String)
    cm_name = Column(String)
    cm_working_group = Column(String)
    cm_info = Column(JSON)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )
    cm_working_group_focus_area = Column(String)


class ChaossUser(Base):
    __tablename__ = "chaoss_user"
    __table_args__ = {"schema": "augur_data"}

    chaoss_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.chaoss_user_chaoss_id_seq'::regclass)"
        ),
    )
    chaoss_login_name = Column(String)
    chaoss_login_hashword = Column(String)
    chaoss_email = Column(String, unique=True)
    chaoss_text_phone = Column(String)
    chaoss_first_name = Column(String)
    chaoss_last_name = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(True, 6), server_default=text("now()"))


class ContributorAffiliation(Base):
    __tablename__ = "contributor_affiliations"
    __table_args__ = {
        "schema": "augur_data",
        "comment": "This table exists outside of relations with other tables. The purpose is to provide a dynamic, owner maintained (and augur augmented) list of affiliations. This table is processed in affiliation information in the DM_ tables generated when Augur is finished counting commits using the Facade Worker. ",
    }

    ca_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.contributor_affiliations_ca_id_seq'::regclass)"
        ),
    )
    ca_domain = Column(String(64), nullable=False, unique=True)
    ca_start_date = Column(Date, server_default=text("'1970-01-01'::date"))
    ca_last_used = Column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    ca_affiliation = Column(String)
    ca_active = Column(SmallInteger, server_default=text("1"))
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )


class Contributor(Base):
    __tablename__ = "contributors"
    __table_args__ = (
        # add uniques explitcitly, they were inline before
        UniqueConstraint('gh_login', name='GH-UNIQUE-C', initially="DEFERRED", deferrable=True),
        UniqueConstraint('gl_id', name='GL-UNIQUE-B', initially="DEFERRED", deferrable=True),

        # unique key for gitlab users on insertion
        UniqueConstraint('gl_username', name='GL-UNIQUE-C', initially="DEFERRED", deferrable=True),
        UniqueConstraint('cntrb_login', name='GL-cntrb-LOGIN-UNIQUE'),


        # changed from inline to not inline
        Index("cnt-fullname", "cntrb_full_name", postgresql_using='hash'),
        Index("cntrb-theemail", "cntrb_email", postgresql_using='hash'),
        Index("contributors_idx_cntrb_email3", "cntrb_email"),
        Index("cntrb_canonica-idx11", "cntrb_canonical"),
        Index("cntrb_login_platform_index", "cntrb_login"),


        # added
        Index("contributor_worker_email_finder", "cntrb_email", postgresql_using='brin'),
        Index("contributor_worker_fullname_finder", "cntrb_full_name", postgresql_using='brin'),

        Index("login", "cntrb_login"),
        Index("login-contributor-idx", "cntrb_login"),

        {
            "schema": "augur_data",
            "comment": "For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login. \nGithub now allows a user to change their login name, but their user id remains the same in this case. So, the natural key is the combination of id and login, but there should never be repeated logins. ",
        },
    )

    cntrb_id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text(
            "nextval('augur_data.contributors_cntrb_id_seq'::regclass)"
        ),
    )
    cntrb_login = Column(
        String,
        comment="Will be a double population with the same value as gh_login for github, but the local value for other systems. ",
    )
    cntrb_email = Column(
        String,
        comment="This needs to be here for matching contributor ids, which are augur, to the commit information. ",
    )
    cntrb_full_name = Column(String)
    cntrb_company = Column(String)
    cntrb_created_at = Column(TIMESTAMP(precision=0))
    cntrb_type = Column(
        String, comment="Present in another models. It is not currently used in Augur. "
    )
    cntrb_fake = Column(SmallInteger, server_default=text("0"))
    cntrb_deleted = Column(SmallInteger, server_default=text("0"))
    cntrb_long = Column(Numeric(11, 8), server_default=text("NULL::numeric"))
    cntrb_lat = Column(Numeric(10, 8), server_default=text("NULL::numeric"))
    cntrb_country_code = Column(CHAR(3), server_default=text("NULL::bpchar"))
    cntrb_state = Column(String)
    cntrb_city = Column(String)
    cntrb_location = Column(String)
    cntrb_canonical = Column(String)
    cntrb_last_used = Column(
        TIMESTAMP(True, 0), server_default=text("NULL::timestamp with time zone")
    )
    gh_user_id = Column(BigInteger)
    gh_login = Column(
        String,
        comment="populated with the github user name for github originated data. ",
    )
    gh_url = Column(String)
    gh_html_url = Column(String)
    gh_node_id = Column(String)
    gh_avatar_url = Column(String)
    gh_gravatar_id = Column(String)
    gh_followers_url = Column(String)
    gh_following_url = Column(String)
    gh_gists_url = Column(String)
    gh_starred_url = Column(String)
    gh_subscriptions_url = Column(String)
    gh_organizations_url = Column(String)
    gh_repos_url = Column(String)
    gh_events_url = Column(String)
    gh_received_events_url = Column(String)
    gh_type = Column(String)
    gh_site_admin = Column(String)
    gl_web_url = Column(
        String,
        comment='“web_url” value from these API calls to GitLab, all for the same user\n\nhttps://gitlab.com/api/v4/users?username=computationalmystic\nhttps://gitlab.com/api/v4/users?search=s@goggins.com\nhttps://gitlab.com/api/v4/users?search=outdoors@acm.org\n\n[\n  {\n    "id": 5481034,\n    "name": "sean goggins",\n    "username": "computationalmystic",\n    "state": "active",\n    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",\n    "web_url": "https://gitlab.com/computationalmystic"\n  }\n]',
    )
    gl_avatar_url = Column(
        String,
        comment='“avatar_url” value from these API calls to GitLab, all for the same user\n\nhttps://gitlab.com/api/v4/users?username=computationalmystic\nhttps://gitlab.com/api/v4/users?search=s@goggins.com\nhttps://gitlab.com/api/v4/users?search=outdoors@acm.org\n\n[\n  {\n    "id": 5481034,\n    "name": "sean goggins",\n    "username": "computationalmystic",\n    "state": "active",\n    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",\n    "web_url": "https://gitlab.com/computationalmystic"\n  }\n]',
    )
    gl_state = Column(
        String,
        comment='“state” value from these API calls to GitLab, all for the same user\n\nhttps://gitlab.com/api/v4/users?username=computationalmystic\nhttps://gitlab.com/api/v4/users?search=s@goggins.com\nhttps://gitlab.com/api/v4/users?search=outdoors@acm.org\n\n[\n  {\n    "id": 5481034,\n    "name": "sean goggins",\n    "username": "computationalmystic",\n    "state": "active",\n    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",\n    "web_url": "https://gitlab.com/computationalmystic"\n  }\n]',
    )
    gl_username = Column(
        String,
        comment='“username” value from these API calls to GitLab, all for the same user\n\nhttps://gitlab.com/api/v4/users?username=computationalmystic\nhttps://gitlab.com/api/v4/users?search=s@goggins.com\nhttps://gitlab.com/api/v4/users?search=outdoors@acm.org\n\n[\n  {\n    "id": 5481034,\n    "name": "sean goggins",\n    "username": "computationalmystic",\n    "state": "active",\n    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",\n    "web_url": "https://gitlab.com/computationalmystic"\n  }\n]',
    )
    gl_full_name = Column(
        String,
        comment='“name” value from these API calls to GitLab, all for the same user\n\nhttps://gitlab.com/api/v4/users?username=computationalmystic\nhttps://gitlab.com/api/v4/users?search=s@goggins.com\nhttps://gitlab.com/api/v4/users?search=outdoors@acm.org\n\n[\n  {\n    "id": 5481034,\n    "name": "sean goggins",\n    "username": "computationalmystic",\n    "state": "active",\n    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",\n    "web_url": "https://gitlab.com/computationalmystic"\n  }\n]',
    )
    gl_id = Column(
        BigInteger,
        comment='"id" value from these API calls to GitLab, all for the same user\n\nhttps://gitlab.com/api/v4/users?username=computationalmystic\nhttps://gitlab.com/api/v4/users?search=s@goggins.com\nhttps://gitlab.com/api/v4/users?search=outdoors@acm.org\n\n[\n  {\n    "id": 5481034,\n    "name": "sean goggins",\n    "username": "computationalmystic",\n    "state": "active",\n    "avatar_url": "https://secure.gravatar.com/avatar/fb1fb43953a6059df2fe8d94b21d575c?s=80&d=identicon",\n    "web_url": "https://gitlab.com/computationalmystic"\n  }\n]',
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )


t_dm_repo_annual = Table(
    "dm_repo_annual",
    metadata,
    Column("repo_id", BigInteger, nullable=False),
    Column("email", String, nullable=False),
    Column("affiliation", String, server_default=text("'NULL'::character varying")),
    Column("year", SmallInteger, nullable=False),
    Column("added", BigInteger, nullable=False),
    Column("removed", BigInteger, nullable=False),
    Column("whitespace", BigInteger, nullable=False),
    Column("files", BigInteger, nullable=False),
    Column("patches", BigInteger, nullable=False),
    Column("tool_source", String),
    Column("tool_version", String),
    Column("data_source", String),
    Column(
        "data_collection_date",
        TIMESTAMP(precision=0),
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("repo_id,email_copy_1", "repo_id", "email"),
    Index("repo_id,affiliation_copy_1", "repo_id", "affiliation"),
    schema="augur_data",
)


t_dm_repo_group_annual = Table(
    "dm_repo_group_annual",
    metadata,
    Column("repo_group_id", BigInteger, nullable=False),
    Column("email", String, nullable=False),
    Column("affiliation", String, server_default=text("'NULL'::character varying")),
    Column("year", SmallInteger, nullable=False),
    Column("added", BigInteger, nullable=False),
    Column("removed", BigInteger, nullable=False),
    Column("whitespace", BigInteger, nullable=False),
    Column("files", BigInteger, nullable=False),
    Column("patches", BigInteger, nullable=False),
    Column("tool_source", String),
    Column("tool_version", String),
    Column("data_source", String),
    Column(
        "data_collection_date",
        TIMESTAMP(precision=0),
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("projects_id,email_copy_1", "repo_group_id", "email"),
    Index("projects_id,affiliation_copy_1", "repo_group_id", "affiliation"),
    schema="augur_data",
)


t_dm_repo_group_monthly = Table(
    "dm_repo_group_monthly",
    metadata,
    Column("repo_group_id", BigInteger, nullable=False),
    Column("email", String, nullable=False),
    Column("affiliation", String, server_default=text("'NULL'::character varying")),
    Column("month", SmallInteger, nullable=False),
    Column("year", SmallInteger, nullable=False),
    Column("added", BigInteger, nullable=False),
    Column("removed", BigInteger, nullable=False),
    Column("whitespace", BigInteger, nullable=False),
    Column("files", BigInteger, nullable=False),
    Column("patches", BigInteger, nullable=False),
    Column("tool_source", String),
    Column("tool_version", String),
    Column("data_source", String),
    Column(
        "data_collection_date",
        TIMESTAMP(precision=0),
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("projects_id,year,email_copy_1", "repo_group_id", "year", "email"),
    Index("projects_id,affiliation_copy_2", "repo_group_id", "affiliation"),
    Index("projects_id,email_copy_2", "repo_group_id", "email"),
    Index(
        "projects_id,year,affiliation_copy_1", "repo_group_id", "year", "affiliation"
    ),
    schema="augur_data",
)


t_dm_repo_group_weekly = Table(
    "dm_repo_group_weekly",
    metadata,
    Column("repo_group_id", BigInteger, nullable=False),
    Column("email", String, nullable=False),
    Column("affiliation", String, server_default=text("'NULL'::character varying")),
    Column("week", SmallInteger, nullable=False),
    Column("year", SmallInteger, nullable=False),
    Column("added", BigInteger, nullable=False),
    Column("removed", BigInteger, nullable=False),
    Column("whitespace", BigInteger, nullable=False),
    Column("files", BigInteger, nullable=False),
    Column("patches", BigInteger, nullable=False),
    Column("tool_source", String),
    Column("tool_version", String),
    Column("data_source", String),
    Column(
        "data_collection_date",
        TIMESTAMP(precision=0),
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("projects_id,affiliation", "repo_group_id", "affiliation"),
    Index("projects_id,email", "repo_group_id", "email"),
    Index("projects_id,year,email", "repo_group_id", "year", "email"),
    Index("projects_id,year,affiliation", "repo_group_id", "year", "affiliation"),
    schema="augur_data",
)


t_dm_repo_monthly = Table(
    "dm_repo_monthly",
    metadata,
    Column("repo_id", BigInteger, nullable=False),
    Column("email", String, nullable=False),
    Column("affiliation", String, server_default=text("'NULL'::character varying")),
    Column("month", SmallInteger, nullable=False),
    Column("year", SmallInteger, nullable=False),
    Column("added", BigInteger, nullable=False),
    Column("removed", BigInteger, nullable=False),
    Column("whitespace", BigInteger, nullable=False),
    Column("files", BigInteger, nullable=False),
    Column("patches", BigInteger, nullable=False),
    Column("tool_source", String),
    Column("tool_version", String),
    Column("data_source", String),
    Column(
        "data_collection_date",
        TIMESTAMP(precision=0),
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("repo_id,year,email_copy_1", "repo_id", "year", "email"),
    Index("repo_id,year,affiliation_copy_1", "repo_id", "year", "affiliation"),
    Index("repo_id,affiliation_copy_2", "repo_id", "affiliation"),
    Index("repo_id,email_copy_2", "repo_id", "email"),
    schema="augur_data",
)


t_dm_repo_weekly = Table(
    "dm_repo_weekly",
    metadata,
    Column("repo_id", BigInteger, nullable=False),
    Column("email", String, nullable=False),
    Column("affiliation", String, server_default=text("'NULL'::character varying")),
    Column("week", SmallInteger, nullable=False),
    Column("year", SmallInteger, nullable=False),
    Column("added", BigInteger, nullable=False),
    Column("removed", BigInteger, nullable=False),
    Column("whitespace", BigInteger, nullable=False),
    Column("files", BigInteger, nullable=False),
    Column("patches", BigInteger, nullable=False),
    Column("tool_source", String),
    Column("tool_version", String),
    Column("data_source", String),
    Column(
        "data_collection_date",
        TIMESTAMP(precision=0),
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("repo_id,affiliation", "repo_id", "affiliation"),
    Index("repo_id,email", "repo_id", "email"),
    Index("repo_id,year,email", "repo_id", "year", "email"),
    Index("repo_id,year,affiliation", "repo_id", "year", "affiliation"),
    schema="augur_data",
)


class Exclude(Base):
    __tablename__ = "exclude"
    __table_args__ = {"schema": "augur_data"}

    id = Column(Integer, primary_key=True)
    projects_id = Column(Integer, nullable=False)
    email = Column(String, server_default=text("'NULL'::character varying"))
    domain = Column(String, server_default=text("'NULL'::character varying"))


class LstmAnomalyModel(Base):
    __tablename__ = "lstm_anomaly_models"
    __table_args__ = {"schema": "augur_data"}

    model_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.lstm_anomaly_models_model_id_seq'::regclass)"
        ),
    )
    model_name = Column(String)
    model_description = Column(String)
    look_back_days = Column(BigInteger)
    training_days = Column(BigInteger)
    batch_size = Column(BigInteger)
    metric = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP")
    )


class Platform(Base):
    __tablename__ = "platform"
    __table_args__ = (
        Index("plat", "pltfrm_id", unique=True),
        {"schema": "augur_data"}
    )

    pltfrm_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('augur_data.platform_pltfrm_id_seq'::regclass)"),
    )
    pltfrm_name = Column(String)
    pltfrm_version = Column(String)
    pltfrm_release_date = Column(Date)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0))


class RepoGroup(Base):
    __tablename__ = "repo_groups"
    __table_args__ = (
        Index("rgidm", "repo_group_id", unique=True),
        Index("rgnameindex", "rg_name"),
        {"schema": "augur_data",
        "comment": "rg_type is intended to be either a GitHub Organization or a User Created Repo Group. "},
    )

    repo_group_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_groups_repo_group_id_seq'::regclass)"
        ),
    )
    rg_name = Column(String, nullable=False)
    rg_description = Column(String, server_default=text("'NULL'::character varying"))
    rg_website = Column(String(128), server_default=text("'NULL'::character varying"))
    rg_recache = Column(SmallInteger, server_default=text("1"))
    rg_last_modified = Column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    rg_type = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0))


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
    Index("repos_id,status", "repos_id", "status"),
    Index("repos_id,statusops", "repos_id", "status"),
    schema="augur_data",
)


class Settings(Base):
    __tablename__ = "settings"
    __table_args__ = {"schema": "augur_data"}

    id = Column(Integer, primary_key=True)
    setting = Column(String(32), nullable=False)
    value = Column(String, nullable=False)
    last_modified = Column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


class TopicWord(Base):
    __tablename__ = "topic_words"
    __table_args__ = {"schema": "augur_data"}

    topic_words_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.topic_words_topic_words_id_seq'::regclass)"
        ),
    )
    topic_id = Column(BigInteger)
    word = Column(String)
    word_prob = Column(Float(53))
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )


t_unknown_cache = Table(
    "unknown_cache",
    metadata,
    Column("type", String(10), nullable=False),
    Column("repo_group_id", Integer, nullable=False),
    Column("email", String(128), nullable=False),
    Column("domain", String(128), server_default=text("'NULL'::character varying")),
    Column("added", BigInteger, nullable=False),
    Column("tool_source", String),
    Column("tool_version", String),
    Column("data_source", String),
    Column(
        "data_collection_date",
        TIMESTAMP(precision=0),
        server_default=text("CURRENT_TIMESTAMP"),
    ),
    Index("type,projects_id", "type", "repo_group_id"),
    schema="augur_data",
)


class UnresolvedCommitEmail(Base):
    __tablename__ = "unresolved_commit_emails"
    __table_args__ = {"schema": "augur_data"}

    email_unresolved_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.unresolved_commit_emails_email_unresolved_id_seq'::regclass)"
        ),
    )
    email = Column(String, nullable=False, unique=True)
    name = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )


class UtilityLog(Base):
    __tablename__ = "utility_log"
    __table_args__ = {"schema": "augur_data"}

    id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('augur_data.utility_log_id_seq1'::regclass)"),
    )
    level = Column(String(8), nullable=False)
    status = Column(String, nullable=False)
    attempted = Column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )


t_working_commits = Table(
    "working_commits",
    metadata,
    Column("repos_id", Integer, nullable=False),
    Column(
        "working_commit", String(40), server_default=text("'NULL'::character varying")
    ),
    schema="augur_data",
)


class ContributorRepo(Base):
    __tablename__ = "contributor_repo"
    __table_args__ = (
        UniqueConstraint("event_id", "tool_version"),
        {
            "schema": "augur_data",
            "comment": 'Developed in Partnership with Andrew Brain. \nFrom: [\n  {\n    "login": "octocat",\n    "id": 1,\n    "node_id": "MDQ6VXNlcjE=",\n    "avatar_url": "https://github.com/images/error/octocat_happy.gif",\n    "gravatar_id": "",\n    "url": "https://api.github.com/users/octocat",\n    "html_url": "https://github.com/octocat",\n    "followers_url": "https://api.github.com/users/octocat/followers",\n    "following_url": "https://api.github.com/users/octocat/following{/other_user}",\n    "gists_url": "https://api.github.com/users/octocat/gists{/gist_id}",\n    "starred_url": "https://api.github.com/users/octocat/starred{/owner}{/repo}",\n    "subscriptions_url": "https://api.github.com/users/octocat/subscriptions",\n    "organizations_url": "https://api.github.com/users/octocat/orgs",\n    "repos_url": "https://api.github.com/users/octocat/repos",\n    "events_url": "https://api.github.com/users/octocat/events{/privacy}",\n    "received_events_url": "https://api.github.com/users/octocat/received_events",\n    "type": "User",\n    "site_admin": false\n  }\n]\n',
        },
    )

    cntrb_repo_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.contributor_repo_cntrb_repo_id_seq'::regclass)"
        ),
    )
    cntrb_id = Column(
        ForeignKey(
            "augur_data.contributors.cntrb_id", ondelete="RESTRICT", onupdate="CASCADE"
        ),
        nullable=False,
        comment="This is not null because what is the point without the contributor in this table? ",
    )
    repo_git = Column(
        String,
        nullable=False,
        comment="Similar to cntrb_id, we need this data for the table to have meaningful data. ",
    )
    repo_name = Column(String, nullable=False)
    gh_repo_id = Column(BigInteger, nullable=False)
    cntrb_category = Column(String)
    event_id = Column(BigInteger)
    created_at = Column(TIMESTAMP(precision=0))
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship("Contributor")


class ContributorsAlias(Base):
    __tablename__ = "contributors_aliases"
    __table_args__ = (
        UniqueConstraint("alias_email", "canonical_email"),
        {
            "schema": "augur_data",
            "comment": "Every open source user may have more than one email used to make contributions over time. Augur selects the first email it encounters for a user as its “canonical_email”. \n\nThe canonical_email is also added to the contributors_aliases table, with the canonical_email and alias_email being identical.  Using this strategy, an email search will only need to join the alias table for basic email information, and can then more easily map the canonical email from each alias row to the same, more detailed information in the contributors table for a user. ",
        },
    )

    cntrb_alias_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.contributors_aliases_cntrb_alias_id_seq'::regclass)"
        ),
    )
    cntrb_id = Column(
        ForeignKey(
            "augur_data.contributors.cntrb_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        ),
        nullable=False,
    )
    canonical_email = Column(String, nullable=False)
    alias_email = Column(String, nullable=False)
    cntrb_active = Column(SmallInteger, nullable=False, server_default=text("1"))
    cntrb_last_modified = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship("Contributor")


class Repo(Base):
    __tablename__ = "repo"
    __table_args__ = (
        UniqueConstraint("repo_git", name="repo_git-unique"),

        Index("forked", "forked_from"),
        Index("repo_idx_repo_id_repo_namex", "repo_id", "repo_name"),
        Index("repogitindexrep", "repo_git"),

        Index("reponameindex", "repo_name", postgresql_using='hash'),

        Index("reponameindexbtree", "repo_name"),
        Index("rggrouponrepoindex", "repo_group_id"),
        Index("therepo", "repo_id", unique=True),

        {
            "schema": "augur_data",
            "comment": "This table is a combination of the columns in Facade’s repo table and GHTorrent’s projects table. ",
        },
    )

    repo_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('augur_data.repo_repo_id_seq'::regclass)"),
    )
    repo_group_id = Column(
        ForeignKey("augur_data.repo_groups.repo_group_id"), nullable=False
    )
    repo_git = Column(String, nullable=False)
    repo_path = Column(String, server_default=text("'NULL'::character varying"))
    repo_name = Column(
        String, server_default=text("'NULL'::character varying")
    )
    repo_added = Column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    repo_status = Column(
        String, nullable=False, server_default=text("'New'::character varying")
    )
    repo_type = Column(
        String,
        server_default=text("''::character varying"),
        comment='This field is intended to indicate if the repository is the "main instance" of a repository in cases where implementations choose to add the same repository to more than one repository group. In cases where the repository group is of rg_type Github Organization then this repo_type should be "primary". In other cases the repo_type should probably be "user created". We made this a varchar in order to hold open the possibility that there are additional repo_types we have not thought about. ',
    )
    url = Column(String)
    owner_id = Column(Integer)
    description = Column(String)
    primary_language = Column(String)
    created_at = Column(String)
    forked_from = Column(String)
    updated_at = Column(TIMESTAMP(precision=0))
    repo_archived_date_collected = Column(TIMESTAMP(True, 0))
    repo_archived = Column(Integer)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo_group = relationship("RepoGroup")


class RepoTestCoverage(Base):
    __tablename__ = "repo_test_coverage"
    __table_args__ = {"schema": "augur_data"}

    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id"),
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_test_coverage_repo_id_seq'::regclass)"
        ),
    )
    repo_clone_date = Column(TIMESTAMP(precision=0))
    rtc_analysis_date = Column(TIMESTAMP(precision=0))
    programming_language = Column(String)
    file_path = Column(String)
    file_name = Column(String)
    testing_tool = Column(String)
    file_statement_count = Column(BigInteger)
    file_subroutine_count = Column(BigInteger)
    file_statements_tested = Column(BigInteger)
    file_subroutines_tested = Column(BigInteger)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )


class RepoGroupInsight(Base):
    __tablename__ = "repo_group_insights"
    __table_args__ = {
        "schema": "augur_data",
        "comment": 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a REPOSITORY_GROUP and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. \n\nWorker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ',
    }

    rgi_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_group_insights_rgi_id_seq'::regclass)"
        ),
    )
    repo_group_id = Column(ForeignKey("augur_data.repo_groups.repo_group_id"))
    rgi_metric = Column(String)
    rgi_value = Column(String)
    cms_id = Column(BigInteger)
    rgi_fresh = Column(
        Boolean,
        comment='false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ',
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo_group = relationship("RepoGroup")


class RepoGroupsListServe(Base):
    __tablename__ = "repo_groups_list_serve"
    __table_args__ = (
        UniqueConstraint("rgls_id", "repo_group_id"),
        Index("lister", "rgls_id", "repo_group_id", unique=True),
        {"schema": "augur_data"},
    )

    rgls_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_groups_list_serve_rgls_id_seq'::regclass)"
        ),
    )
    repo_group_id = Column(
        ForeignKey("augur_data.repo_groups.repo_group_id"), nullable=False
    )
    rgls_name = Column(String)
    rgls_description = Column(String(3000))
    rgls_sponsor = Column(String)
    rgls_email = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0))

    repo_group = relationship("RepoGroup")


class Commit(Base):
    __tablename__ = "commits"
    __table_args__ = (
        # DB
        Index("author_affiliation", "cmt_author_affiliation"),
        Index("author_cntrb_id", "cmt_ght_author_id"),
        Index("author_raw_email", "cmt_author_raw_email"),
        Index("commited", "cmt_id"),
        Index(
            "commits_idx_cmt_email_cmt_date_cmt_name",
            "cmt_author_email",
            "cmt_author_date",
            "cmt_author_name",
        ),
        Index("committer_affiliation", "cmt_committer_affiliation",
                 postgresql_using='hash'),

        Index(
            "author_email,author_affiliation,author_date",
            "cmt_author_email",
            "cmt_author_affiliation",
            "cmt_author_date",
        ),
        Index("committer_raw_email", "cmt_committer_raw_email"),
        Index("repo_id,commit", "repo_id", "cmt_commit_hash"),

        {
            "schema": "augur_data",
            "comment": "Commits.\nEach row represents changes to one FILE within a single commit. So you will encounter multiple rows per commit hash in many cases. ",
        },
    )

    cmt_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('augur_data.commits_cmt_id_seq'::regclass)"),
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    cmt_commit_hash = Column(String(80), nullable=False)
    cmt_author_name = Column(String, nullable=False)
    cmt_author_raw_email = Column(String, nullable=False)
    cmt_author_email = Column(String, nullable=False)
    cmt_author_date = Column(String(10), nullable=False)
    cmt_author_affiliation = Column(
        String, server_default=text("'NULL'::character varying")
    )
    cmt_committer_name = Column(String, nullable=False)
    cmt_committer_raw_email = Column(String, nullable=False)
    cmt_committer_email = Column(String, nullable=False)
    cmt_committer_date = Column(String, nullable=False)
    cmt_committer_affiliation = Column(
        String, server_default=text("'NULL'::character varying")
    )
    cmt_added = Column(Integer, nullable=False)
    cmt_removed = Column(Integer, nullable=False)
    cmt_whitespace = Column(Integer, nullable=False)
    cmt_filename = Column(String, nullable=False)
    cmt_date_attempted = Column(TIMESTAMP(precision=0), nullable=False)
    cmt_ght_author_id = Column(Integer)
    cmt_ght_committer_id = Column(Integer)
    cmt_ght_committed_at = Column(TIMESTAMP(precision=0))
    cmt_committer_timestamp = Column(TIMESTAMP(True, 0))
    cmt_author_timestamp = Column(TIMESTAMP(True, 0))
    cmt_author_platform_username = Column(
        ForeignKey(
            "augur_data.contributors.cntrb_login",
            name="fk_commits_contributors_3",
            ondelete="CASCADE",
            onupdate="CASCADE",
            initially="DEFERRED",
            deferrable=True,
        ),
        ForeignKey(
            "augur_data.contributors.cntrb_login",
            name="fk_commits_contributors_4",
            ondelete="CASCADE",
            onupdate="CASCADE",
            initially="DEFERRED",
            deferrable=True,
        ),
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    contributor = relationship(
        "Contributor",
        primaryjoin="Commit.cmt_author_platform_username == Contributor.cntrb_login",
    )
    contributor1 = relationship(
        "Contributor",
        primaryjoin="Commit.cmt_author_platform_username == Contributor.cntrb_login",
    )
    repo = relationship("Repo")


class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (
        Index("issue-cntrb-dix2", "cntrb_id"),
        Index("issues_ibfk_1", "repo_id"),
        Index("issues_ibfk_2", "reporter_id"),
        Index("issues_ibfk_4", "pull_request_id"),

        UniqueConstraint("repo_id", "gh_issue_id"),
        UniqueConstraint("issue_url", name="issue-insert-unique"),
        {"schema": "augur_data"},
    )

    issue_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('augur_data.issue_seq'::regclass)"),
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="CASCADE", onupdate="CASCADE"),
    )
    reporter_id = Column(
        ForeignKey("augur_data.contributors.cntrb_id"),
        comment="The ID of the person who opened the issue. ",
    )
    pull_request = Column(BigInteger)
    pull_request_id = Column(BigInteger)
    created_at = Column(TIMESTAMP(precision=0))
    issue_title = Column(String)
    issue_body = Column(String)
    cntrb_id = Column(
        ForeignKey("augur_data.contributors.cntrb_id"),
        comment="The ID of the person who closed the issue. ",
    )
    comment_count = Column(BigInteger)
    updated_at = Column(TIMESTAMP(precision=0))
    closed_at = Column(TIMESTAMP(precision=0))
    due_on = Column(TIMESTAMP(precision=0))
    repository_url = Column(String)
    issue_url = Column(String)
    labels_url = Column(String)
    comments_url = Column(String)
    events_url = Column(String)
    html_url = Column(String)
    issue_state = Column(String)
    issue_node_id = Column(String)
    gh_issue_number = Column(BigInteger)
    gh_issue_id = Column(BigInteger)
    gh_user_id = Column(BigInteger)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship(
        "Contributor", primaryjoin="Issue.cntrb_id == Contributor.cntrb_id"
    )
    repo = relationship("Repo")
    reporter = relationship(
        "Contributor", primaryjoin="Issue.reporter_id == Contributor.cntrb_id"
    )


class Library(Base):
    __tablename__ = "libraries"
    __table_args__ = {"schema": "augur_data"}

    library_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('augur_data.libraries_library_id_seq'::regclass)"),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    platform = Column(String)
    name = Column(String)
    created_timestamp = Column(
        TIMESTAMP(precision=0), server_default=text("NULL::timestamp without time zone")
    )
    updated_timestamp = Column(
        TIMESTAMP(precision=0), server_default=text("NULL::timestamp without time zone")
    )
    library_description = Column(
        String(2000), server_default=text("NULL::character varying")
    )
    keywords = Column(String)
    library_homepage = Column(
        String(1000), server_default=text("NULL::character varying")
    )
    license = Column(String)
    version_count = Column(Integer)
    latest_release_timestamp = Column(String)
    latest_release_number = Column(String)
    package_manager_id = Column(String)
    dependency_count = Column(Integer)
    dependent_library_count = Column(Integer)
    primary_language = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0))

    repo = relationship("Repo")


class LstmAnomalyResult(Base):
    __tablename__ = "lstm_anomaly_results"
    __table_args__ = {"schema": "augur_data"}

    result_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.lstm_anomaly_results_result_id_seq'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    repo_category = Column(String)
    model_id = Column(ForeignKey("augur_data.lstm_anomaly_models.model_id"))
    metric = Column(String)
    contamination_factor = Column(Float(53))
    mean_absolute_error = Column(Float(53))
    remarks = Column(String)
    metric_field = Column(
        String,
        comment="This is a listing of all of the endpoint fields included in the generation of the metric. Sometimes there is one, sometimes there is more than one. This will list them all. ",
    )
    mean_absolute_actual_value = Column(Float(53))
    mean_absolute_prediction_value = Column(Float(53))
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP")
    )

    model = relationship("LstmAnomalyModel")
    repo = relationship("Repo")


class Message(Base):
    __tablename__ = "message"
    __table_args__ = (
        UniqueConstraint("platform_msg_id", name="message-insert-unique"),
        Index("msg-cntrb-id-idx", "cntrb_id"),
        Index("platformgrouper", "msg_id", "pltfrm_id"),
        Index("messagegrouper", "msg_id", "rgls_id", unique=True),
        {"schema": "augur_data"},
    )

    msg_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('augur_data.message_msg_id_seq'::regclass)"),
    )
    rgls_id = Column(
        ForeignKey(
            "augur_data.repo_groups_list_serve.rgls_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    platform_msg_id = Column(BigInteger)
    platform_node_id = Column(String)
    repo_id = Column(
        ForeignKey(
            "augur_data.repo.repo_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    cntrb_id = Column(
        ForeignKey(
            "augur_data.contributors.cntrb_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        comment="Not populated for mailing lists. Populated for GitHub issues. ",
    )
    msg_text = Column(String)
    msg_timestamp = Column(TIMESTAMP(precision=0))
    msg_sender_email = Column(String)
    msg_header = Column(String)
    pltfrm_id = Column(
        ForeignKey(
            "augur_data.platform.pltfrm_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship("Contributor")
    pltfrm = relationship("Platform")
    repo = relationship("Repo")
    rgls = relationship("RepoGroupsListServe")


class MessageAnalysisSummary(Base):
    __tablename__ = "message_analysis_summary"
    __table_args__ = {
        "schema": "augur_data",
        "comment": "In a relationally perfect world, we would have a table called “message_analysis_run” the incremented the “worker_run_id” for both message_analysis and message_analysis_summary. For now, we decided this was overkill. ",
    }

    msg_summary_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.message_analysis_summary_msg_summary_id_seq'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    worker_run_id = Column(
        BigInteger,
        comment='This value should reflect the worker_run_id for the messages summarized in the table. There is not a relation between these two tables for that purpose because its not *really*, relationaly a concept unless we create a third table for "worker_run_id", which we determined was unnecessarily complex. ',
    )
    positive_ratio = Column(Float(53))
    negative_ratio = Column(Float(53))
    novel_count = Column(
        BigInteger,
        comment="The number of messages identified as novel during the analyzed period",
    )
    period = Column(
        TIMESTAMP(precision=0),
        comment="The whole timeline is divided into periods based on the definition of time period for analysis, which is user specified. Timestamp of the first period to look at, until the end of messages at the data of execution. ",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo = relationship("Repo")


class MessageSentimentSummary(Base):
    __tablename__ = "message_sentiment_summary"
    __table_args__ = {
        "schema": "augur_data",
        "comment": "In a relationally perfect world, we would have a table called “message_sentiment_run” the incremented the “worker_run_id” for both message_sentiment and message_sentiment_summary. For now, we decided this was overkill. ",
    }

    msg_summary_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.message_sentiment_summary_msg_summary_id_seq'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    worker_run_id = Column(
        BigInteger,
        comment='This value should reflect the worker_run_id for the messages summarized in the table. There is not a relation between these two tables for that purpose because its not *really*, relationaly a concept unless we create a third table for "worker_run_id", which we determined was unnecessarily complex. ',
    )
    positive_ratio = Column(Float(53))
    negative_ratio = Column(Float(53))
    novel_count = Column(
        BigInteger,
        comment="The number of messages identified as novel during the analyzed period",
    )
    period = Column(
        TIMESTAMP(precision=0),
        comment="The whole timeline is divided into periods based on the definition of time period for analysis, which is user specified. Timestamp of the first period to look at, until the end of messages at the data of execution. ",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo = relationship("Repo")


class PullRequest(Base):
    __tablename__ = "pull_requests"
    __table_args__ = (
        UniqueConstraint("repo_id", "pr_src_id", name="unique-pr"),
        UniqueConstraint("repo_id", "pr_src_id", name="unique-prx"),
        UniqueConstraint("pr_url", name="pull-request-insert-unique"),
        Index("id_node", "pr_src_id", "pr_src_node_id"),
        Index(
            "pull_requests_idx_repo_id_data_datex", "repo_id", "data_collection_date"
        ),
        {"schema": "augur_data"},
    )

    pull_request_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_requests_pull_request_id_seq'::regclass)"
        ),
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="CASCADE", onupdate="CASCADE"),
        server_default=text("0"),
    )
    pr_url = Column(String)
    pr_src_id = Column(
        BigInteger, comment="The pr_src_id is unique across all of github."
    )
    pr_src_node_id = Column(String)
    pr_html_url = Column(String)
    pr_diff_url = Column(String)
    pr_patch_url = Column(String)
    pr_issue_url = Column(String)
    pr_augur_issue_id = Column(
        BigInteger, comment="This is to link to the augur stored related issue"
    )
    pr_src_number = Column(
        BigInteger, comment="The pr_src_number is unique within a repository."
    )
    pr_src_state = Column(String)
    pr_src_locked = Column(Boolean)
    pr_src_title = Column(String)
    pr_augur_contributor_id = Column(
        ForeignKey(
            "augur_data.contributors.cntrb_id", ondelete="RESTRICT", onupdate="CASCADE"
        ),
        comment="This is to link to the augur contributor record. ",
    )
    pr_body = Column(Text)
    pr_created_at = Column(TIMESTAMP(precision=0))
    pr_updated_at = Column(TIMESTAMP(precision=0))
    pr_closed_at = Column(TIMESTAMP(precision=0))
    pr_merged_at = Column(TIMESTAMP(precision=0))
    pr_merge_commit_sha = Column(String)
    pr_teams = Column(BigInteger, comment="One to many with pull request teams. ")
    pr_milestone = Column(String)
    pr_commits_url = Column(String)
    pr_review_comments_url = Column(String)
    pr_review_comment_url = Column(
        String,
        comment="This is a field with limited utility. It does expose how to access a specific comment if needed with parameters. If the source changes URL structure, it may be useful",
    )
    pr_comments_url = Column(String)
    pr_statuses_url = Column(String)
    pr_meta_head_id = Column(
        String,
        comment="The metadata for the head repo that links to the pull_request_meta table. ",
    )
    pr_meta_base_id = Column(
        String,
        comment="The metadata for the base repo that links to the pull_request_meta table. ",
    )
    pr_src_issue_url = Column(String)
    pr_src_comments_url = Column(String)
    pr_src_review_comments_url = Column(String)
    pr_src_commits_url = Column(String)
    pr_src_statuses_url = Column(String)
    pr_src_author_association = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    pr_augur_contributor = relationship("Contributor")
    repo = relationship("Repo")


class Release(Base):
    __tablename__ = "releases"
    __table_args__ = {"schema": "augur_data"}

    release_id = Column(
        CHAR(64),
        primary_key=True,
        server_default=text("nextval('augur_data.releases_release_id_seq'::regclass)"),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"), nullable=False)
    release_name = Column(String)
    release_description = Column(String)
    release_author = Column(String)
    release_created_at = Column(TIMESTAMP(precision=6))
    release_published_at = Column(TIMESTAMP(precision=6))
    release_updated_at = Column(TIMESTAMP(precision=6))
    release_is_draft = Column(Boolean)
    release_is_prerelease = Column(Boolean)
    release_tag_name = Column(String)
    release_url = Column(String)
    tag_only = Column(Boolean)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=6), server_default=text("CURRENT_TIMESTAMP")
    )

    repo = relationship("Repo")


class RepoBadging(Base):
    __tablename__ = "repo_badging"
    __table_args__ = {
        "schema": "augur_data",
        "comment": "This will be collected from the LF’s Badging API\nhttps://bestpractices.coreinfrastructure.org/projects.json?pq=https%3A%2F%2Fgithub.com%2Fchaoss%2Faugur\n",
    }

    badge_collection_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_badging_badge_collection_id_seq'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    created_at = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )
    data = Column(JSONB(astext_type=Text()))

    repo = relationship("Repo")


class RepoClusterMessage(Base):
    __tablename__ = "repo_cluster_messages"
    __table_args__ = {"schema": "augur_data"}

    msg_cluster_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_cluster_messages_msg_cluster_id_seq'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    cluster_content = Column(Integer)
    cluster_mechanism = Column(Integer)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo = relationship("Repo")


class RepoDependency(Base):
    __tablename__ = "repo_dependencies"
    __table_args__ = {
        "schema": "augur_data",
        "comment": "Contains the dependencies for a repo.",
    }

    repo_dependencies_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_dependencies_repo_dependencies_id_seq'::regclass)"
        ),
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id"), comment="Forign key for repo id. "
    )
    dep_name = Column(String, comment="Name of the dependancy found in project. ")
    dep_count = Column(Integer, comment="Number of times the dependancy was found. ")
    dep_language = Column(String, comment="Language of the dependancy. ")
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo = relationship("Repo")


class RepoDepsLibyear(Base):
    __tablename__ = "repo_deps_libyear"
    __table_args__ = {"schema": "augur_data"}

    repo_deps_libyear_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_deps_libyear_repo_deps_libyear_id_seq'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    name = Column(String)
    requirement = Column(String)
    type = Column(String)
    package_manager = Column(String)
    current_verion = Column(String)
    latest_version = Column(String)
    current_release_date = Column(String)
    latest_release_date = Column(String)
    libyear = Column(Float(53))
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo = relationship("Repo")


class RepoDepsScorecard(Base):
    __tablename__ = "repo_deps_scorecard"
    __table_args__ = {"schema": "augur_data"}

    repo_deps_scorecard_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_deps_scorecard_repo_deps_scorecard_id_seq1'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    name = Column(String)
    status = Column(String)
    score = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo = relationship("Repo")


class RepoInfo(Base):
    __tablename__ = "repo_info"
    __table_args__ = (
        Index("repo_info_idx_repo_id_data_date_1x", "repo_id", "data_collection_date"),
        Index("repo_info_idx_repo_id_data_datex", "repo_id", "data_collection_date"),
        {"schema": "augur_data"},
    )

    repo_info_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_info_repo_info_id_seq'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"), nullable=False)
    last_updated = Column(
        TIMESTAMP(precision=0), server_default=text("NULL::timestamp without time zone")
    )
    issues_enabled = Column(String)
    open_issues = Column(Integer)
    pull_requests_enabled = Column(String)
    wiki_enabled = Column(String)
    pages_enabled = Column(String)
    fork_count = Column(Integer)
    default_branch = Column(String)
    watchers_count = Column(Integer)
    UUID = Column(Integer)
    license = Column(String)
    stars_count = Column(Integer)
    committers_count = Column(Integer)
    issue_contributors_count = Column(String)
    changelog_file = Column(String)
    contributing_file = Column(String)
    license_file = Column(String)
    code_of_conduct_file = Column(String)
    security_issue_file = Column(String)
    security_audit_file = Column(String)
    status = Column(String)
    keywords = Column(String)
    commit_count = Column(BigInteger)
    issues_count = Column(BigInteger)
    issues_closed = Column(BigInteger)
    pull_request_count = Column(BigInteger)
    pull_requests_open = Column(BigInteger)
    pull_requests_closed = Column(BigInteger)
    pull_requests_merged = Column(BigInteger)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo = relationship("Repo")


class RepoInsight(Base):
    __tablename__ = "repo_insights"
    __table_args__ = {
        "schema": "augur_data",
        "comment": 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a repository and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. \n\nWorker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ',
    }

    ri_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text("nextval('augur_data.repo_insights_ri_id_seq'::regclass)"),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    ri_metric = Column(String)
    ri_value = Column(String)
    ri_date = Column(TIMESTAMP(precision=0))
    ri_fresh = Column(
        Boolean,
        comment='false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ',
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )
    ri_score = Column(Numeric)
    ri_field = Column(String)
    ri_detection_method = Column(String)

    repo = relationship("Repo")


class RepoInsightsRecord(Base):
    __tablename__ = "repo_insights_records"
    __table_args__ = (
        Index("dater", "ri_date"),
        {"schema": "augur_data"}
    )

    ri_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_insights_records_ri_id_seq'::regclass)"
        ),
        comment="Primary key. ",
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="SET NULL", onupdate="CASCADE"),
        comment="Refers to repo table primary key. Will have a foreign key",
    )
    ri_metric = Column(String, comment="The metric endpoint")
    ri_field = Column(String, comment="The field in the metric endpoint")
    ri_value = Column(String, comment="The value of the endpoint in ri_field")
    ri_date = Column(
        TIMESTAMP(precision=6),
        comment="The date the insight is for; in other words, some anomaly occurred on this date. ",
    )
    ri_score = Column(Float(53), comment="A Score, derived from the algorithm used. ")
    ri_detection_method = Column(
        String,
        comment='A confidence interval or other expression of the type of threshold and the value of a threshold met in order for it to be "an insight". Example. "95% confidence interval". ',
    )
    tool_source = Column(String, comment="Standard Augur Metadata")
    tool_version = Column(String, comment="Standard Augur Metadata")
    data_source = Column(String, comment="Standard Augur Metadata")
    data_collection_date = Column(
        TIMESTAMP(precision=6),
        server_default=text("CURRENT_TIMESTAMP"),
        comment="Standard Augur Metadata",
    )

    repo = relationship("Repo")


class RepoLabor(Base):
    __tablename__ = "repo_labor"
    __table_args__ = (
        UniqueConstraint("repo_id", "rl_analysis_date", "file_path", "file_name"),
        {
            "schema": "augur_data",
            "comment": "repo_labor is a derivative of tables used to store scc code and complexity counting statistics that are inputs to labor analysis, which are components of CHAOSS value metric calculations. ",
        },
    )

    repo_labor_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_labor_repo_labor_id_seq'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    repo_clone_date = Column(TIMESTAMP(precision=0))
    rl_analysis_date = Column(TIMESTAMP(precision=0))
    programming_language = Column(String)
    file_path = Column(String)
    file_name = Column(String)
    total_lines = Column(Integer)
    code_lines = Column(Integer)
    comment_lines = Column(Integer)
    blank_lines = Column(Integer)
    code_complexity = Column(Integer)
    repo_url = Column(
        String,
        comment="This is a convenience column to simplify analysis against external datasets",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0))

    repo = relationship("Repo")


class RepoMeta(Base):
    __tablename__ = "repo_meta"
    __table_args__ = {"schema": "augur_data", "comment": "Project Languages"}

    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id"), primary_key=True, nullable=False
    )
    rmeta_id = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
        server_default=text("nextval('augur_data.repo_meta_rmeta_id_seq'::regclass)"),
    )
    rmeta_name = Column(String)
    rmeta_value = Column(String, server_default=text("0"))
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0))

    repo = relationship("Repo")


class RepoSbomScan(Base):
    __tablename__ = "repo_sbom_scans"
    __table_args__ = {"schema": "augur_data"}

    rsb_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_sbom_scans_rsb_id_seq'::regclass)"
        ),
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="CASCADE", onupdate="CASCADE")
    )
    sbom_scan = Column(JSON)

    repo = relationship("Repo")


class RepoStat(Base):
    __tablename__ = "repo_stats"
    __table_args__ = {"schema": "augur_data", "comment": "Project Watchers"}

    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id"), primary_key=True, nullable=False
    )
    rstat_id = Column(
        BigInteger,
        primary_key=True,
        nullable=False,
        server_default=text("nextval('augur_data.repo_stats_rstat_id_seq'::regclass)"),
    )
    rstat_name = Column(String(400))
    rstat_value = Column(BigInteger)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0))

    repo = relationship("Repo")


class RepoTopic(Base):
    __tablename__ = "repo_topic"
    __table_args__ = {"schema": "augur_data"}

    repo_topic_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.repo_topic_repo_topic_id_seq'::regclass)"
        ),
    )
    repo_id = Column(ForeignKey("augur_data.repo.repo_id"))
    topic_id = Column(Integer)
    topic_prob = Column(Float(53))
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    repo = relationship("Repo")


class CommitCommentRef(Base):
    __tablename__ = "commit_comment_ref"
    __table_args__ = (
        Index("comment_id", "cmt_comment_src_id", "cmt_comment_id", "msg_id"),
        {"schema": "augur_data"},
    )

    cmt_comment_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.commit_comment_ref_cmt_comment_id_seq'::regclass)"
        ),
    )
    cmt_id = Column(
        ForeignKey(
            "augur_data.commits.cmt_id", ondelete="RESTRICT", onupdate="CASCADE"
        ),
        nullable=False,
    )
    repo_id = Column(BigInteger)
    msg_id = Column(
        ForeignKey(
            "augur_data.message.msg_id", ondelete="RESTRICT", onupdate="CASCADE"
        ),
        nullable=False,
    )
    user_id = Column(BigInteger, nullable=False)
    body = Column(Text)
    line = Column(BigInteger)
    position = Column(BigInteger)
    commit_comment_src_node_id = Column(
        String,
        comment="For data provenance, we store the source node ID if it exists. ",
    )
    cmt_comment_src_id = Column(
        BigInteger,
        nullable=False,
        unique=True,
        comment="For data provenance, we store the source ID if it exists. ",
    )
    created_at = Column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cmt = relationship("Commit")
    msg = relationship("Message")


class CommitParent(Base):
    __tablename__ = "commit_parents"
    __table_args__ = (
        Index("commit_parents_ibfk_1", "cmt_id"),
        Index("commit_parents_ibfk_2", "parent_id"),
        {"schema": "augur_data"}
    )

    cmt_id = Column(
        ForeignKey("augur_data.commits.cmt_id"),
        primary_key=True,
        nullable=False,
    )
    parent_id = Column(
        ForeignKey("augur_data.commits.cmt_id"),
        primary_key=True,
        nullable=False,
        server_default=text(
            "nextval('augur_data.commit_parents_parent_id_seq'::regclass)"
        ),
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cmt = relationship("Commit", primaryjoin="CommitParent.cmt_id == Commit.cmt_id")
    parent = relationship(
        "Commit", primaryjoin="CommitParent.parent_id == Commit.cmt_id"
    )


class DiscourseInsight(Base):
    __tablename__ = "discourse_insights"
    __table_args__ = {
        "schema": "augur_data",
        "comment": "This table is populated by the “Discourse_Analysis_Worker”. It examines sequential discourse, using computational linguistic methods, to draw statistical inferences regarding the discourse in a particular comment thread. ",
    }

    msg_discourse_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.discourse_insights_msg_discourse_id_seq1'::regclass)"
        ),
    )
    msg_id = Column(ForeignKey("augur_data.message.msg_id"))
    discourse_act = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(True, 6), server_default=text("CURRENT_TIMESTAMP")
    )

    msg = relationship("Message")


class IssueAssignee(Base):
    __tablename__ = "issue_assignees"
    __table_args__ = (
        Index("issue-cntrb-assign-idx-1", "cntrb_id"),
        UniqueConstraint("issue_assignee_src_id", "issue_id", name="issue-assignee-insert-unique"),
        {"schema": "augur_data"}
    )

    issue_assignee_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.issue_assignees_issue_assignee_id_seq'::regclass)"
        ),
    )
    issue_id = Column(ForeignKey("augur_data.issues.issue_id"))
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    cntrb_id = Column(ForeignKey("augur_data.contributors.cntrb_id"))
    issue_assignee_src_id = Column(
        BigInteger,
        comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.",
    )
    issue_assignee_src_node = Column(
        String,
        comment="This character based identifier comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship("Contributor")
    issue = relationship("Issue")
    repo = relationship("Repo")


class IssueEvent(Base):
    __tablename__ = "issue_events"
    __table_args__ = (
        UniqueConstraint('issue_id', 'issue_event_src_id', name='unique_event_id_key'),

        Index("issue-cntrb-idx2", "issue_event_src_id"),
        Index("issue_events_ibfk_1", "issue_id"),
        Index("issue_events_ibfk_2", "cntrb_id"),

        {"schema": "augur_data"},
    )

    event_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.issue_events_event_id_seq'::regclass)"
        ),
    )
    issue_id = Column(
        ForeignKey(
            "augur_data.issues.issue_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
        nullable=False,
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    cntrb_id = Column(
        ForeignKey(
            "augur_data.contributors.cntrb_id", ondelete="RESTRICT", onupdate="CASCADE"
        ),
        nullable=False,
    )
    action = Column(String, nullable=False)
    action_commit_hash = Column(String)
    created_at = Column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    node_id = Column(
        String,
        comment="This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.",
    )
    node_url = Column(String)
    platform_id = Column(
        ForeignKey(
            "augur_data.platform.pltfrm_id", ondelete="RESTRICT", onupdate="CASCADE"
        ),
        nullable=False,
    )
    issue_event_src_id = Column(
        BigInteger,
        comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship("Contributor")
    issue = relationship("Issue")
    platform = relationship("Platform")
    repo = relationship("Repo")


class IssueLabel(Base):
    __tablename__ = "issue_labels"
    __table_args__ = (
        UniqueConstraint("label_src_id", "issue_id"),
        {"schema": "augur_data"},
    )

    issue_label_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.issue_labels_issue_label_id_seq'::regclass)"
        ),
    )
    issue_id = Column(
        ForeignKey("augur_data.issues.issue_id", ondelete="CASCADE", onupdate="CASCADE")
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    label_text = Column(String)
    label_description = Column(String)
    label_color = Column(String)
    label_src_id = Column(
        BigInteger,
        comment="This character based identifier (node) comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API JSON subsection for issues.",
    )
    label_src_node_id = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    issue = relationship("Issue")
    repo = relationship("Repo")


class IssueMessageRef(Base):
    __tablename__ = "issue_message_ref"
    __table_args__ = (
        UniqueConstraint("issue_msg_ref_src_comment_id", "issue_id", name="issue-message-ref-insert-unique"),
        {"schema": "augur_data"},
    )

    issue_msg_ref_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.issue_message_ref_issue_msg_ref_id_seq'::regclass)"
        ),
    )
    issue_id = Column(
        ForeignKey(
            "augur_data.issues.issue_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    repo_id = Column(
        ForeignKey(
            "augur_data.repo.repo_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    msg_id = Column(
        ForeignKey(
            "augur_data.message.msg_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    issue_msg_ref_src_node_id = Column(
        String,
        comment="This character based identifier comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API",
    )
    issue_msg_ref_src_comment_id = Column(
        BigInteger,
        comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    issue = relationship("Issue")
    msg = relationship("Message")
    repo = relationship("Repo")


class LibraryDependency(Base):
    __tablename__ = "library_dependencies"
    __table_args__ = (
        Index("REPO_DEP", "library_id"),
        {"schema": "augur_data"}
    )

    lib_dependency_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.library_dependencies_lib_dependency_id_seq'::regclass)"
        ),
    )
    library_id = Column(ForeignKey("augur_data.libraries.library_id"))
    manifest_platform = Column(String)
    manifest_filepath = Column(
        String(1000), server_default=text("NULL::character varying")
    )
    manifest_kind = Column(String)
    repo_id_branch = Column(String, nullable=False)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0))

    library = relationship("Library")


class LibraryVersion(Base):
    __tablename__ = "library_version"
    __table_args__ = {"schema": "augur_data"}

    library_version_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.library_version_library_version_id_seq'::regclass)"
        ),
    )
    library_id = Column(ForeignKey("augur_data.libraries.library_id"))
    library_platform = Column(String)
    version_number = Column(String)
    version_release_date = Column(
        TIMESTAMP(precision=0), server_default=text("NULL::timestamp without time zone")
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(TIMESTAMP(precision=0))

    library = relationship("Library")


class MessageAnalysis(Base):
    __tablename__ = "message_analysis"
    __table_args__ = {"schema": "augur_data"}

    msg_analysis_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.message_analysis_msg_analysis_id_seq'::regclass)"
        ),
    )
    msg_id = Column(ForeignKey("augur_data.message.msg_id"))
    worker_run_id = Column(
        BigInteger,
        comment="This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ",
    )
    sentiment_score = Column(
        Float(53),
        comment="A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ",
    )
    reconstruction_error = Column(
        Float(53),
        comment="Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.",
    )
    novelty_flag = Column(
        Boolean,
        comment="This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ",
    )
    feedback_flag = Column(
        Boolean,
        comment="This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    msg = relationship("Message")


class MessageSentiment(Base):
    __tablename__ = "message_sentiment"
    __table_args__ = {"schema": "augur_data"}

    msg_analysis_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.message_sentiment_msg_analysis_id_seq'::regclass)"
        ),
    )
    msg_id = Column(ForeignKey("augur_data.message.msg_id"))
    worker_run_id = Column(
        BigInteger,
        comment="This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ",
    )
    sentiment_score = Column(
        Float(53),
        comment="A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ",
    )
    reconstruction_error = Column(
        Float(53),
        comment="Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.",
    )
    novelty_flag = Column(
        Boolean,
        comment="This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ",
    )
    feedback_flag = Column(
        Boolean,
        comment="This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    msg = relationship("Message")


class PullRequestAnalysis(Base):

    pull_request_analysis_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_analysis_pull_request_analysis_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        comment="It would be better if the pull request worker is run first to fetch the latest PRs before analyzing",
    )
    merge_probability = Column(
        Numeric(256, 250),
        comment="Indicates the probability of the PR being merged",
    )
    mechanism = Column(
        String,
        comment="the ML model used for prediction (It is XGBoost Classifier at present)",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(True, 6), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # metadata is specified down here so the index can reference the column and use .desc().nullslast()
    __tablename__ = "pull_request_analysis"
    __table_args__ = (
        Index("pr_anal_idx", pull_request_id),
        Index("probability_idx", merge_probability.desc().nullslast()),
        {"schema": "augur_data"}
    )

    pull_request = relationship("PullRequest")


class PullRequestAssignee(Base):
    __tablename__ = "pull_request_assignees"
    __table_args__ = (
        Index("pr_meta_cntrb-idx", "contrib_id"),
        UniqueConstraint("pull_request_id", "pr_assignee_src_id", name="assigniees-unique"),
        {"schema": "augur_data"}
    )

    pr_assignee_map_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_assignees_pr_assignee_map_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    repo_id = Column(
        ForeignKey(
            "augur_data.repo.repo_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    contrib_id = Column(ForeignKey("augur_data.contributors.cntrb_id"))
    pr_assignee_src_id = Column(BigInteger)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    contrib = relationship("Contributor")
    pull_request = relationship("PullRequest")
    repo = relationship("Repo")


class PullRequestCommit(Base):
    __tablename__ = "pull_request_commits"
    __table_args__ = (
        UniqueConstraint("pull_request_id", "repo_id", "pr_cmt_sha"),
        {
            "schema": "augur_data",
            "comment": "Pull request commits are an enumeration of each commit associated with a pull request. \nNot all pull requests are from a branch or fork into master. \nThe commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).\nTherefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. \nIn cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ",
        },
    )

    pr_cmt_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_commits_pr_cmt_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    pr_cmt_sha = Column(
        String,
        comment="This is the commit SHA for a pull request commit. If the PR is not to the master branch of the main repository (or, in rare cases, from it), then you will NOT find a corresponding commit SHA in the commit table. (see table comment for further explanation). ",
    )
    pr_cmt_node_id = Column(String)
    pr_cmt_message = Column(String)
    pr_cmt_comments_url = Column(String)
    pr_cmt_author_cntrb_id = Column(
        ForeignKey(
            "augur_data.contributors.cntrb_id", ondelete="CASCADE", onupdate="CASCADE"
        )
    )
    pr_cmt_timestamp = Column(TIMESTAMP(precision=0))
    pr_cmt_author_email = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    pr_cmt_author_cntrb = relationship("Contributor")
    pull_request = relationship("PullRequest")
    repo = relationship("Repo")


class PullRequestEvent(Base):
    __tablename__ = "pull_request_events"
    __table_args__ = (
        Index("pr_events_ibfk_1", "pull_request_id"),
        Index("pr_events_ibfk_2", "cntrb_id"),
        UniqueConstraint("platform_id", "node_id", name="unique-pr-event-id"),
        UniqueConstraint("node_id", name="pr-unqiue-event"),
        {"schema": "augur_data"},
    )

    pr_event_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_events_pr_event_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    repo_id = Column(
        ForeignKey(
            "augur_data.repo.repo_id",
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    cntrb_id = Column(
        ForeignKey("augur_data.contributors.cntrb_id"), nullable=False
    )
    action = Column(String, nullable=False)
    action_commit_hash = Column(String)
    created_at = Column(
        TIMESTAMP(precision=0), nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    issue_event_src_id = Column(
        BigInteger,
        comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API",
    )
    node_id = Column(
        String,
        comment="This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.",
    )
    node_url = Column(String)
    platform_id = Column(
        ForeignKey(
            "augur_data.platform.pltfrm_id",
            ondelete="RESTRICT",
            onupdate="RESTRICT",
            deferrable=True,
            initially="DEFERRED",
        ),
        nullable=False,
        server_default=text("25150"),
    )
    pr_platform_event_id = Column(BigInteger)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship("Contributor")
    platform = relationship("Platform")
    pull_request = relationship("PullRequest")
    repo = relationship("Repo")


class PullRequestFile(Base):
    __tablename__ = "pull_request_files"
    __table_args__ = (
        UniqueConstraint("pull_request_id", "repo_id", "pr_file_path"),
        {
            "schema": "augur_data",
            "comment": "Pull request commits are an enumeration of each commit associated with a pull request. \nNot all pull requests are from a branch or fork into master. \nThe commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).\nTherefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. \nIn cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ",
        },
    )

    pr_file_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_files_pr_file_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    repo_id = Column(
        ForeignKey(
            "augur_data.repo.repo_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    pr_file_additions = Column(BigInteger)
    pr_file_deletions = Column(BigInteger)
    pr_file_path = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    pull_request = relationship("PullRequest")
    repo = relationship("Repo")


class PullRequestLabel(Base):
    __tablename__ = "pull_request_labels"
    __table_args__ = (
        UniqueConstraint("pr_src_id", "pull_request_id"),
        {"schema": "augur_data"},
    )

    pr_label_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_labels_pr_label_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    pr_src_id = Column(BigInteger)
    pr_src_node_id = Column(String)
    pr_src_url = Column(String)
    pr_src_description = Column(String)
    pr_src_color = Column(String)
    pr_src_default_bool = Column(Boolean)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    pull_request = relationship("PullRequest")
    repo = relationship("Repo")


class PullRequestMessageRef(Base):
    __tablename__ = "pull_request_message_ref"
    __table_args__ = (
        UniqueConstraint("pr_message_ref_src_comment_id", "pull_request_id", name="pull-request-message-ref-insert-unique"),
        {"schema": "augur_data"},
    )

    pr_msg_ref_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_message_ref_pr_msg_ref_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    msg_id = Column(
        ForeignKey(
            "augur_data.message.msg_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    pr_message_ref_src_comment_id = Column(BigInteger)
    pr_message_ref_src_node_id = Column(String)
    pr_issue_url = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    msg = relationship("Message")
    pull_request = relationship("PullRequest")
    repo = relationship("Repo")


class PullRequestMeta(Base):
    __tablename__ = "pull_request_meta"
    __table_args__ = (
        Index("pr_meta-cntrbid-idx", "cntrb_id"),
        UniqueConstraint("pull_request_id", "pr_head_or_base", 'pr_sha', name="pull-request-meta-insert-unique"),
        {"schema": "augur_data",
        "comment": 'Pull requests contain referencing metadata.  There are a few columns that are discrete. There are also head and base designations for the repo on each side of the pull request. Similar functions exist in GitLab, though the language here is based on GitHub. The JSON Being adapted to as of the development of this schema is here:      "base": {       "label": "chaoss:dev",       "ref": "dev",       "sha": "dc6c6f3947f7dc84ecba3d8bda641ef786e7027d",       "user": {         "login": "chaoss",         "id": 29740296,         "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",         "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",         "gravatar_id": "",         "url": "https://api.github.com/users/chaoss",         "html_url": "https://github.com/chaoss",         "followers_url": "https://api.github.com/users/chaoss/followers",         "following_url": "https://api.github.com/users/chaoss/following{/other_user}",         "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",         "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",         "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",         "organizations_url": "https://api.github.com/users/chaoss/orgs",         "repos_url": "https://api.github.com/users/chaoss/repos",         "events_url": "https://api.github.com/users/chaoss/events{/privacy}",         "received_events_url": "https://api.github.com/users/chaoss/received_events",         "type": "Organization",         "site_admin": false       },       "repo": {         "id": 78134122,         "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",         "name": "augur",         "full_name": "chaoss/augur",         "private": false,         "owner": {           "login": "chaoss",           "id": 29740296,           "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",           "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",           "gravatar_id": "",           "url": "https://api.github.com/users/chaoss",           "html_url": "https://github.com/chaoss",           "followers_url": "https://api.github.com/users/chaoss/followers",           "following_url": "https://api.github.com/users/chaoss/following{/other_user}",           "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",           "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",           "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",           "organizations_url": "https://api.github.com/users/chaoss/orgs",           "repos_url": "https://api.github.com/users/chaoss/repos",           "events_url": "https://api.github.com/users/chaoss/events{/privacy}",           "received_events_url": "https://api.github.com/users/chaoss/received_events",           "type": "Organization",           "site_admin": false         }, '},
    )

    pr_repo_meta_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_meta_pr_repo_meta_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    repo_id = Column(
        ForeignKey(
            "augur_data.repo.repo_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    pr_head_or_base = Column(
        String,
        comment="Each pull request should have one and only one head record; and one and only one base record. ",
    )
    pr_src_meta_label = Column(
        String,
        comment='This is a representation of the repo:branch information in the pull request. Head is issueing the pull request and base is taking the pull request. For example:  (We do not store all of this)\n\n "head": {\n      "label": "chaoss:pull-request-worker",\n      "ref": "pull-request-worker",\n      "sha": "6b380c3d6d625616f79d702612ebab6d204614f2",\n      "user": {\n        "login": "chaoss",\n        "id": 29740296,\n        "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",\n        "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",\n        "gravatar_id": "",\n        "url": "https://api.github.com/users/chaoss",\n        "html_url": "https://github.com/chaoss",\n        "followers_url": "https://api.github.com/users/chaoss/followers",\n        "following_url": "https://api.github.com/users/chaoss/following{/other_user}",\n        "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",\n        "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",\n        "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",\n        "organizations_url": "https://api.github.com/users/chaoss/orgs",\n        "repos_url": "https://api.github.com/users/chaoss/repos",\n        "events_url": "https://api.github.com/users/chaoss/events{/privacy}",\n        "received_events_url": "https://api.github.com/users/chaoss/received_events",\n        "type": "Organization",\n        "site_admin": false\n      },\n      "repo": {\n        "id": 78134122,\n        "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",\n        "name": "augur",\n        "full_name": "chaoss/augur",\n        "private": false,\n        "owner": {\n          "login": "chaoss",\n          "id": 29740296,\n          "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",\n          "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",\n          "gravatar_id": "",\n          "url": "https://api.github.com/users/chaoss",\n          "html_url": "https://github.com/chaoss",\n          "followers_url": "https://api.github.com/users/chaoss/followers",\n          "following_url": "https://api.github.com/users/chaoss/following{/other_user}",\n          "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",\n          "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",\n          "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",\n          "organizations_url": "https://api.github.com/users/chaoss/orgs",\n          "repos_url": "https://api.github.com/users/chaoss/repos",\n          "events_url": "https://api.github.com/users/chaoss/events{/privacy}",\n          "received_events_url": "https://api.github.com/users/chaoss/received_events",\n          "type": "Organization",\n          "site_admin": false\n        },\n        "html_url": "https://github.com/chaoss/augur",\n        "description": "Python library and web service for Open Source Software Health and Sustainability metrics & data collection.",\n        "fork": false,\n        "url": "https://api.github.com/repos/chaoss/augur",\n        "forks_url": "https://api.github.com/repos/chaoss/augur/forks",\n        "keys_url": "https://api.github.com/repos/chaoss/augur/keys{/key_id}",\n        "collaborators_url": "https://api.github.com/repos/chaoss/augur/collaborators{/collaborator}",\n        "teams_url": "https://api.github.com/repos/chaoss/augur/teams",\n        "hooks_url": "https://api.github.com/repos/chaoss/augur/hooks",\n        "issue_events_url": "https://api.github.com/repos/chaoss/augur/issues/events{/number}",\n        "events_url": "https://api.github.com/repos/chaoss/augur/events",\n        "assignees_url": "https://api.github.com/repos/chaoss/augur/assignees{/user}",\n        "branches_url": "https://api.github.com/repos/chaoss/augur/branches{/branch}",\n        "tags_url": "https://api.github.com/repos/chaoss/augur/tags",\n        "blobs_url": "https://api.github.com/repos/chaoss/augur/git/blobs{/sha}",\n        "git_tags_url": "https://api.github.com/repos/chaoss/augur/git/tags{/sha}",\n        "git_refs_url": "https://api.github.com/repos/chaoss/augur/git/refs{/sha}",\n        "trees_url": "https://api.github.com/repos/chaoss/augur/git/trees{/sha}",\n        "statuses_url": "https://api.github.com/repos/chaoss/augur/statuses/{sha}",\n        "languages_url": "https://api.github.com/repos/chaoss/augur/languages",\n        "stargazers_url": "https://api.github.com/repos/chaoss/augur/stargazers",\n        "contributors_url": "https://api.github.com/repos/chaoss/augur/contributors",\n        "subscribers_url": "https://api.github.com/repos/chaoss/augur/subscribers",\n        "subscription_url": "https://api.github.com/repos/chaoss/augur/subscription",\n        "commits_url": "https://api.github.com/repos/chaoss/augur/commits{/sha}",\n        "git_commits_url": "https://api.github.com/repos/chaoss/augur/git/commits{/sha}",\n        "comments_url": "https://api.github.com/repos/chaoss/augur/comments{/number}",\n        "issue_comment_url": "https://api.github.com/repos/chaoss/augur/issues/comments{/number}",\n        "contents_url": "https://api.github.com/repos/chaoss/augur/contents/{+path}",\n        "compare_url": "https://api.github.com/repos/chaoss/augur/compare/{base}...{head}",\n        "merges_url": "https://api.github.com/repos/chaoss/augur/merges",\n        "archive_url": "https://api.github.com/repos/chaoss/augur/{archive_format}{/ref}",\n        "downloads_url": "https://api.github.com/repos/chaoss/augur/downloads",\n        "issues_url": "https://api.github.com/repos/chaoss/augur/issues{/number}",\n        "pulls_url": "https://api.github.com/repos/chaoss/augur/pulls{/number}",\n        "milestones_url": "https://api.github.com/repos/chaoss/augur/milestones{/number}",\n        "notifications_url": "https://api.github.com/repos/chaoss/augur/notifications{?since,all,participating}",\n        "labels_url": "https://api.github.com/repos/chaoss/augur/labels{/name}",\n        "releases_url": "https://api.github.com/repos/chaoss/augur/releases{/id}",\n        "deployments_url": "https://api.github.com/repos/chaoss/augur/deployments",\n        "created_at": "2017-01-05T17:34:54Z",\n        "updated_at": "2019-11-15T00:56:12Z",\n        "pushed_at": "2019-12-02T06:27:26Z",\n        "git_url": "git://github.com/chaoss/augur.git",\n        "ssh_url": "git@github.com:chaoss/augur.git",\n        "clone_url": "https://github.com/chaoss/augur.git",\n        "svn_url": "https://github.com/chaoss/augur",\n        "homepage": "http://augur.osshealth.io/",\n        "size": 82004,\n        "stargazers_count": 153,\n        "watchers_count": 153,\n        "language": "Python",\n        "has_issues": true,\n        "has_projects": false,\n        "has_downloads": true,\n        "has_wiki": false,\n        "has_pages": true,\n        "forks_count": 205,\n        "mirror_url": null,\n        "archived": false,\n        "disabled": false,\n        "open_issues_count": 14,\n        "license": {\n          "key": "mit",\n          "name": "MIT License",\n          "spdx_id": "MIT",\n          "url": "https://api.github.com/licenses/mit",\n          "node_id": "MDc6TGljZW5zZTEz"\n        },\n        "forks": 205,\n        "open_issues": 14,\n        "watchers": 153,\n        "default_branch": "master"\n      }\n    },\n    "base": {\n      "label": "chaoss:dev",\n      "ref": "dev",\n      "sha": "bfd2d34b51659613dd842cf83c3873f7699c2a0e",\n      "user": {\n        "login": "chaoss",\n        "id": 29740296,\n        "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",\n        "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",\n        "gravatar_id": "",\n        "url": "https://api.github.com/users/chaoss",\n        "html_url": "https://github.com/chaoss",\n        "followers_url": "https://api.github.com/users/chaoss/followers",\n        "following_url": "https://api.github.com/users/chaoss/following{/other_user}",\n        "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",\n        "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",\n        "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",\n        "organizations_url": "https://api.github.com/users/chaoss/orgs",\n        "repos_url": "https://api.github.com/users/chaoss/repos",\n        "events_url": "https://api.github.com/users/chaoss/events{/privacy}",\n        "received_events_url": "https://api.github.com/users/chaoss/received_events",\n        "type": "Organization",\n        "site_admin": false\n      },\n      "repo": {\n        "id": 78134122,\n        "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",\n        "name": "augur",\n        "full_name": "chaoss/augur",\n        "private": false,\n        "owner": {\n          "login": "chaoss",\n          "id": 29740296,\n          "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",\n          "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",\n          "gravatar_id": "",\n          "url": "https://api.github.com/users/chaoss",\n          "html_url": "https://github.com/chaoss",\n          "followers_url": "https://api.github.com/users/chaoss/followers",\n          "following_url": "https://api.github.com/users/chaoss/following{/other_user}",\n          "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",\n          "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",\n          "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",\n          "organizations_url": "https://api.github.com/users/chaoss/orgs",\n          "repos_url": "https://api.github.com/users/chaoss/repos",\n          "events_url": "https://api.github.com/users/chaoss/events{/privacy}",\n          "received_events_url": "https://api.github.com/users/chaoss/received_events",\n          "type": "Organization",\n          "site_admin": false\n        },\n',
    )
    pr_src_meta_ref = Column(String)
    pr_sha = Column(String)
    cntrb_id = Column(ForeignKey("augur_data.contributors.cntrb_id"))
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship("Contributor")
    pull_request = relationship("PullRequest")
    repo = relationship("Repo")


class PullRequestReviewer(Base):
    __tablename__ = "pull_request_reviewers"
    __table_args__ = (
        Index("pr-reviewers-cntrb-idx1", "cntrb_id"),
        UniqueConstraint("pull_request_id", "pr_reviewer_src_id"),
        {"schema": "augur_data"},
    )

    pr_reviewer_map_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_reviewers_pr_reviewer_map_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    pr_source_id = Column(
        BigInteger,
        comment="The platform ID for the pull/merge request. Used as part of the natural key, along with pr_reviewer_src_id in this table. ",
    )
    repo_id = Column(BigInteger)
    cntrb_id = Column(
        ForeignKey(
            "augur_data.contributors.cntrb_id", ondelete="CASCADE", onupdate="CASCADE"
        ),
    )
    pr_reviewer_src_id = Column(
        BigInteger,
        comment="The platform ID for the pull/merge request reviewer. Used as part of the natural key, along with pr_source_id in this table. ",
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship("Contributor")
    pull_request = relationship("PullRequest")


class PullRequestReview(Base):
    __tablename__ = "pull_request_reviews"
    __table_args__ = (
        UniqueConstraint("pr_review_src_id", "tool_source"),
        {"schema": "augur_data"},
    )

    pr_review_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_reviews_pr_review_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", ondelete="RESTRICT", onupdate="CASCADE")
    )
    cntrb_id = Column(
        ForeignKey(
            "augur_data.contributors.cntrb_id", ondelete="RESTRICT", onupdate="CASCADE"
        ),
        nullable=False,
    )
    pr_review_author_association = Column(String)
    pr_review_state = Column(String)
    pr_review_body = Column(String)
    pr_review_submitted_at = Column(TIMESTAMP(precision=6))
    pr_review_src_id = Column(BigInteger)
    pr_review_node_id = Column(String)
    pr_review_html_url = Column(String)
    pr_review_pull_request_url = Column(String)
    pr_review_commit_id = Column(String)
    platform_id = Column(
        ForeignKey(
            "augur_data.platform.pltfrm_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        ),
        server_default=text("25150"),
    )
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    cntrb = relationship("Contributor")
    platform = relationship("Platform")
    pull_request = relationship("PullRequest")
    repo = relationship("Repo")


class PullRequestTeam(Base):
    __tablename__ = "pull_request_teams"
    __table_args__ = {"schema": "augur_data"}

    pr_team_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_teams_pr_team_id_seq'::regclass)"
        ),
    )
    pull_request_id = Column(
        ForeignKey(
            "augur_data.pull_requests.pull_request_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    pr_src_team_id = Column(BigInteger)
    pr_src_team_node = Column(String)
    pr_src_team_url = Column(String)
    pr_team_name = Column(String)
    pr_team_slug = Column(String)
    pr_team_description = Column(String)
    pr_team_privacy = Column(String)
    pr_team_permission = Column(String)
    pr_team_src_members_url = Column(String)
    pr_team_src_repositories_url = Column(String)
    pr_team_parent_id = Column(BigInteger)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    pull_request = relationship("PullRequest")


class PullRequestRepo(Base):
    __tablename__ = "pull_request_repo"
    __table_args__ = (
        Index("pr-cntrb-idx-repo", "pr_cntrb_id"),
        {"schema": "augur_data",
        "comment": "This table is for storing information about forks that exist as part of a pull request. Generally we do not want to track these like ordinary repositories. "},
    )

    pr_repo_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_repo_pr_repo_id_seq'::regclass)"
        ),
    )
    pr_repo_meta_id = Column(
        ForeignKey(
            "augur_data.pull_request_meta.pr_repo_meta_id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        )
    )
    pr_repo_head_or_base = Column(
        String,
        comment="For ease of validation checking, we should determine if the repository referenced is the head or base of the pull request. Each pull request should have one and only one of these, which is not enforcable easily in the database.",
    )
    pr_src_repo_id = Column(BigInteger)
    pr_src_node_id = Column(String)
    pr_repo_name = Column(String)
    pr_repo_full_name = Column(String)
    pr_repo_private_bool = Column(Boolean)
    pr_cntrb_id = Column(ForeignKey("augur_data.contributors.cntrb_id"))
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    pr_cntrb = relationship("Contributor")
    pr_repo_meta = relationship("PullRequestMeta")


class PullRequestReviewMessageRef(Base):
    __tablename__ = "pull_request_review_message_ref"
    __table_args__ = (
        UniqueConstraint("pr_review_msg_src_id", name="pull-request-review-message-ref-insert-unique"),
        {"schema": "augur_data"},
    )

    pr_review_msg_ref_id = Column(
        BigInteger,
        primary_key=True,
        server_default=text(
            "nextval('augur_data.pull_request_review_message_ref_pr_review_msg_ref_id_seq'::regclass)"
        ),
    )
    pr_review_id = Column(
        ForeignKey(
            "augur_data.pull_request_reviews.pr_review_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        ),
        nullable=False,
    )
    repo_id = Column(
        ForeignKey(
            "augur_data.repo.repo_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        )
    )
    msg_id = Column(
        ForeignKey(
            "augur_data.message.msg_id",
            ondelete="RESTRICT",
            onupdate="CASCADE",
            deferrable=True,
            initially="DEFERRED",
        ),
        nullable=False,
    )
    pr_review_msg_url = Column(String)
    pr_review_src_id = Column(BigInteger)
    pr_review_msg_src_id = Column(BigInteger)
    pr_review_msg_node_id = Column(String)
    pr_review_msg_diff_hunk = Column(String)
    pr_review_msg_path = Column(String)
    pr_review_msg_position = Column(BigInteger)
    pr_review_msg_original_position = Column(BigInteger)
    pr_review_msg_commit_id = Column(String)
    pr_review_msg_original_commit_id = Column(String)
    pr_review_msg_updated_at = Column(TIMESTAMP(precision=6))
    pr_review_msg_html_url = Column(String)
    pr_url = Column(String)
    pr_review_msg_author_association = Column(String)
    pr_review_msg_start_line = Column(BigInteger)
    pr_review_msg_original_start_line = Column(BigInteger)
    pr_review_msg_start_side = Column(String)
    pr_review_msg_line = Column(BigInteger)
    pr_review_msg_original_line = Column(BigInteger)
    pr_review_msg_side = Column(String)
    tool_source = Column(String)
    tool_version = Column(String)
    data_source = Column(String)
    data_collection_date = Column(
        TIMESTAMP(precision=0), server_default=text("CURRENT_TIMESTAMP")
    )

    msg = relationship("Message")
    pr_review = relationship("PullRequestReview")
    repo = relationship("Repo")

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy import Index, UniqueConstraint, PrimaryKeyConstraint, ForeignKeyConstraint, create_engine, func, text
from datetime import datetime
from augur.config import AugurConfig
import os

ROOT_AUGUR_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# Import the flask app
app = Flask(__name__)


config = AugurConfig(ROOT_AUGUR_DIR)

user = config.get_value('Database', 'user')
password = config.get_value('Database', 'password')
host = config.get_value('Database', 'host')
port = config.get_value('Database', 'port')
database = config.get_value('Database', 'database')


DB_STR = 'postgresql://{}:{}@{}:{}/{}'.format(
    user, password, host, port, database)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_STR
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

db = SQLAlchemy(app)
# TODO: Why is there a working_commits and repos_fetch_log in both of the schemas? There classes conflict

# TODO: look at how facade queries it and add index


# TODO: Why is there a working_commits and repos_fetch_log in both of the schemas? There classes conflict

# TODO: look at how facade queries it and add index
# TODO: look at how facade queries it and add index
class AnalysisLog(db.Model):
    analysis_log_id = db.Column(db.BigInteger, primary_key=True)
    repos_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(), nullable=False)
    date_attempted = db.Column(
        db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

    # this is an insert always table so it does not need a UniqueConstraint
    __tablename__ = 'analysis_log'
    __table_args__ = (
        db.Index("repos_id", repos_id),
        {"schema": "augur_data"}
    )

# TODO: Manually filled by db creation script
# TODO: Could revive this table


class ChaossMetricStatus(db.Model):
    cms_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cm_group = db.Column(db.String())
    cm_source = db.Column(db.String())
    cm_type = db.Column(db.String())
    cm_backend_status = db.Column(db.String())
    cm_frontend_status = db.Column(db.String())
    cm_defined = db.Column(db.Boolean())
    cm_api_endpoint_repo = db.Column(db.String())
    cm_api_endpoint_rg = db.Column(db.String())
    cm_name = db.Column(db.String())
    cm_working_group = db.Column(db.String())
    cm_info = db.Column(db.JSON())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())
    cm_working_group_focus_area = db.Column(db.String())

    __tablename__ = 'chaoss_metric_status'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": "This table used to track CHAOSS Metric implementations in Augur, but due to the constantly changing location of that information, it is for the moment not actively populated. "}
    )


class CommitCommentRef(db.Model):
    cmt_comment_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cmt_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.commits.cmt_id',
                       name='fk_commit_comment_ref_commits_1', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    repo_id = db.Column(db.BigInteger)
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id',
                       name='fk_commit_comment_ref_message_1', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    user_id = db.Column(db.BigInteger, nullable=False)
    body = db.Column(db.Text())
    line = db.Column(db.BigInteger)
    position = db.Column(db.BigInteger)
    commit_comment_src_node_id = db.Column(db.String(
    ), comment="For data provenance, we store the source node ID if it exists. ")
    cmt_comment_src_id = db.Column(
        db.BigInteger, nullable=False, comment="For data provenance, we store the source ID if it exists. ")
    created_at = db.Column(db.TIMESTAMP(), nullable=False,
                           server_default=func.current_timestamp())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    message = relationship("Message", back_populates="commit")
    commit = relationship("Commits", back_populates="msg_ref")

    __tablename__ = 'commit_comment_ref'
    __table_args__ = (
        db.Index("comment_id", cmt_comment_src_id, cmt_comment_id, msg_id),

        # unique value for insertion
        UniqueConstraint('cmt_comment_src_id', name='commitcomment'),
        {"schema": "augur_data"}
    )

# TODO: This table does not get used so remove it and test without


class CommitParents(db.Model):
    cmt_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.commits.cmt_id', name='fk_commit_parents_commits_1'), primary_key=True)
    parent_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.commits.cmt_id', name='fk_commit_parents_commits_2'), primary_key=True)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'commit_parents'
    __table_args__ = (
        db.Index("commit_parents_ibfk_1", cmt_id),
        db.Index("commit_parents_ibfk_2", parent_id),
        {"schema": "augur_data"}
    )


# TODO: Add foriegn key: cmt_author_platform_username = db.Column(db.String(), db.ForeignKey('augur_data.contributors.cntrb_login', name='fk_commits_contributors_3', ondelete="CASCADE", onupdate="CASCADE"))
# TODO: Add relationship with this foreign key
class Commits(db.Model):
    cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id',
                        name='fk_commits_repo_2', ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    cmt_commit_hash = db.Column(db.String(), nullable=False)
    cmt_author_name = db.Column(db.String(), nullable=False)
    cmt_author_raw_email = db.Column(db.String(), nullable=False)
    cmt_author_email = db.Column(db.String(), nullable=False)
    cmt_author_date = db.Column(db.String(), nullable=False)
    cmt_author_affiliation = db.Column(db.String(), server_default='NULL')
    cmt_committer_name = db.Column(db.String(), nullable=False)
    cmt_committer_raw_email = db.Column(db.String(), nullable=False)
    cmt_committer_email = db.Column(db.String(), nullable=False)
    cmt_committer_date = db.Column(db.String(), nullable=False)
    cmt_committer_affiliation = db.Column(db.String(), server_default='NULL')
    cmt_added = db.Column(db.Integer, nullable=False)
    cmt_removed = db.Column(db.Integer, nullable=False)
    cmt_whitespace = db.Column(db.Integer, nullable=False)
    cmt_filename = db.Column(db.String(), nullable=False)
    cmt_date_attempted = db.Column(db.TIMESTAMP(), nullable=False)
    cmt_ght_author_id = db.Column(db.Integer)
    cmt_ght_committer_id = db.Column(db.Integer)
    cmt_ght_committed_at = db.Column(db.TIMESTAMP())
    cmt_committer_timestamp = db.Column(db.TIMESTAMP(timezone=True))
    cmt_author_timestamp = db.Column(db.TIMESTAMP(timezone=True))
    # TODO: Appears that this foreign key is duplicated in the database
    cmt_author_platform_username = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    msg_ref = relationship("CommitCommentRef", back_populates="commit")

    def get_messages(self):

        messages = []
        for msg_ref in self.msg_ref:
            messages.append(msg_ref.message)

        return messages

    __tablename__ = 'commits'
    __table_args__ = (
        db.Index("author_affiliation", cmt_author_affiliation,
                 postgresql_using='hash'),
        db.Index("author_cntrb_id", cmt_ght_author_id),
        db.Index("author_email,author_affiliation,author_date",
                 cmt_author_email, cmt_author_affiliation, cmt_author_date),
        db.Index("author_raw_email", cmt_author_raw_email),
        db.Index("cmt-author-date-idx2", cmt_author_date),
        db.Index("cmt_author_contrib_worker", cmt_author_name,
                 cmt_author_email, cmt_author_date, postgresql_using='brin'),
        db.Index("cmt_commiter_contrib_worker", cmt_committer_name,
                 cmt_committer_email, cmt_committer_date, postgresql_using='brin'),
        db.Index("commited", cmt_id),
        db.Index("commits_idx_cmt_email_cmt_date_cmt_name",
                 cmt_author_email, cmt_author_date, cmt_author_name),
        db.Index("commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam", repo_id,
                 cmt_author_email, cmt_author_date, cmt_author_name),
        db.Index("commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam2", repo_id,
                 cmt_committer_email, cmt_committer_date, cmt_committer_name),
        db.Index("committer_affiliation", cmt_committer_affiliation,
                 postgresql_using='hash'),
        db.Index("committer_email,committer_affiliation,committer_date",
                 cmt_committer_email, cmt_committer_affiliation, cmt_committer_date),
        db.Index("committer_raw_email", cmt_committer_raw_email),
        db.Index("repo_id,commit", repo_id, cmt_commit_hash),
        {
            "schema": "augur_data",
            "comment": "Commits.\nEach row represents changes to one FILE within a single commit. So you will encounter multiple rows per commit hash in many cases. "
        }
    )


# Current db has varchar with length but I changed that
class ContributorAffiliations(db.Model):
    ca_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    ca_domain = db.Column(db.String(), nullable=False)
    ca_start_date = db.Column(db.Date, server_default='1970-01-01')
    ca_last_used = db.Column(
        db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())
    ca_affiliation = db.Column(db.String())
    ca_active = db.Column(db.SmallInteger, server_default=text('1'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'contributor_affiliations'
    __table_args__ = (
        UniqueConstraint('ca_domain', name='unique_domain'),
        {"schema": "augur_data",
         "comment": "This table exists outside of relations with other tables. The purpose is to provide a dynamic, owner maintained (and augur augmented) list of affiliations. This table is processed in affiliation information in the DM_ tables generated when Augur is finished counting commits using the Facade Worker. "}
    )

# TODO: Add foreign key to repo table on cntrb_repo_id


class ContributorRepo(db.Model):
    cntrb_repo_id = db.Column(db.BigInteger, nullable=False)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_contributor_repo_contributors_1', ondelete="RESTRICT",
                         onupdate="CASCADE"), nullable=False, comment="This is not null because what is the point without the contributor in this table? ")
    repo_git = db.Column(db.String(), nullable=False,
                         comment="Similar to cntrb_id, we need this data for the table to have meaningful data. ")
    repo_name = db.Column(db.String(), nullable=False)
    gh_repo_id = db.Column(db.BigInteger, nullable=False)
    cntrb_category = db.Column(db.String())
    event_id = db.Column(db.BigInteger)
    created_at = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'contributor_repo'
    __table_args__ = (
        PrimaryKeyConstraint('cntrb_repo_id', name='cntrb_repo_id_key'),

        UniqueConstraint('event_id', 'tool_version', name='eventer'),
        {"schema": "augur_data"}
    )


class Contributors(db.Model):
    cntrb_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cntrb_login = db.Column(db.String(
    ), comment="Will be a double population with the same value as gh_login for github, but the local value for other systems. ")
    cntrb_email = db.Column(db.String(
    ), comment="This needs to be here for matching contributor ids, which are augur, to the commit information. ")
    cntrb_full_name = db.Column(db.String())
    cntrb_company = db.Column(db.String())
    cntrb_created_at = db.Column(db.TIMESTAMP())
    cntrb_type = db.Column(db.String(
    ), comment="Present in another models. It is not currently used in Augur. ")
    cntrb_fake = db.Column(db.SmallInteger, server_default=text('0'))
    cntrb_deleted = db.Column(db.SmallInteger, server_default=text('0'))
    cntrb_long = db.Column(db.Numeric(precision=11, scale=8))
    cntrb_lat = db.Column(db.Numeric(precision=10, scale=8))
    cntrb_country_code = db.Column(db.CHAR(length=3))
    cntrb_state = db.Column(db.String())
    cntrb_city = db.Column(db.String())
    cntrb_location = db.Column(db.String())
    cntrb_canonical = db.Column(db.String())
    cntrb_last_used = db.Column(db.TIMESTAMP(timezone=True))
    gh_user_id = db.Column(db.BigInteger)
    gh_login = db.Column(db.String(
    ), comment="populated with the github user name for github originated data. ")
    gh_url = db.Column(db.String())
    gh_html_url = db.Column(db.String())
    gh_node_id = db.Column(db.String())
    gh_avatar_url = db.Column(db.String())
    gh_gravatar_id = db.Column(db.String())
    gh_followers_url = db.Column(db.String())
    gh_following_url = db.Column(db.String())
    gh_gists_url = db.Column(db.String())
    gh_starred_url = db.Column(db.String())
    gh_subscriptions_url = db.Column(db.String())
    gh_organizations_url = db.Column(db.String())
    gh_repos_url = db.Column(db.String())
    gh_events_url = db.Column(db.String())
    gh_received_events_url = db.Column(db.String())
    gh_type = db.Column(db.String())
    gh_site_admin = db.Column(db.String())
    gl_web_url = db.Column(db.String())
    gl_avatar_url = db.Column(db.String())
    gl_state = db.Column(db.String())
    gl_username = db.Column(db.String())
    gl_full_name = db.Column(db.String())
    gl_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    repos_contributed = relationship("ContributorRepo")
    aliases = relationship("ContributorsAliases")
    messages = relationship("Message")

    __tablename__ = 'contributors'
    __table_args__ = (
        UniqueConstraint('gh_login', name='GH-UNIQUE-C',
                         initially="DEFERRED", deferrable=True),
        UniqueConstraint('gl_id', name='GL-UNIQUE-B',
                         initially="DEFERRED", deferrable=True),

        # unique key for gitlab users on insertion
        UniqueConstraint('gl_username', name='GL-UNIQUE-C',
                         initially="DEFERRED", deferrable=True),

        # unique key to insert on for github
        UniqueConstraint('cntrb_login', name='GL-cntrb-LOGIN-UNIQUE'),

        db.Index("cnt-fullname", cntrb_full_name, postgresql_using='hash'),
        db.Index("cntrb-theemail", cntrb_email, postgresql_using='hash'),

        db.Index("cntrb_canonica-idx11", cntrb_canonical),
        db.Index("cntrb_login_platform_index", cntrb_login),

        db.Index("contributor_delete_finder", cntrb_id,
                 cntrb_email, postgresql_using='brin'),
        db.Index("contributor_worker_email_finder",
                 cntrb_email, postgresql_using='brin'),
        db.Index("contributor_worker_finder", cntrb_login,
                 cntrb_email, cntrb_id, postgresql_using='brin'),

        # TODO: This index is the same as the first one but one has a different stuff
        db.Index("contributor_worker_fullname_finder",
                 cntrb_full_name, postgresql_using='brin'),

        db.Index("contributors_idx_cntrb_email3", cntrb_email),

        # TODO: These last onese appear to be the same
        db.Index("login", cntrb_login),
        db.Index("login-contributor-idx", cntrb_login),

        {"schema": "augur_data",
         "comment": "For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login.\nGithub now allows a user to change their login name, but their user id remains the same in this case. So, the natural key is the combination of id and login, but there should never be repeated logins. "}
    )


class ContributorsAliases(db.Model):
    cntrb_alias_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_contributors_aliases_contributors_1',
                         ondelete="CASCADE", onupdate="CASCADE", initially="DEFERRED", deferrable=True), nullable=False)
    canonical_email = db.Column(db.String(), nullable=False)
    alias_email = db.Column(db.String(), nullable=False)
    cntrb_active = db.Column(
        db.SmallInteger, nullable=False, server_default=text('1'))
    cntrb_last_modified = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'contributors_aliases'
    __table_args__ = (
        UniqueConstraint('alias_email', 'canonical_email',
                         name='only-email-once', initially="DEFERRED", deferrable=True),
        {"schema": "augur_data",
         "comment": 'Every open source user may have more than one email used to make contributions over time. Augur selects the first email it encounters for a user as its “canonical_email”. \n\nThe canonical_email is also added to the contributors_aliases table, with the canonical_email and alias_email being identical.  Using this strategy, an email search will only need to join the alias table for basic email information, and can then more easily map the canonical email from each alias row to the same, more detailed information in the contributors table for a user. '}
    )


# TODO: Add relationship: Don't understand table well enough
class DiscourseInsights(db.Model):
    msg_discourse_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    msg_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.message.msg_id', name='fk_discourse_insights_message_1'))
    discourse_act = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'discourse_insights'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": "This table is populated by the “Discourse_Analysis_Worker”. It examines sequential discourse, using computational linguistic methods, to draw statistical inferences regarding the discourse in a particular comment thread. "}
    )

# TODO: Add foreign keys to repo and repogroups


class DmRepoAnnual(db.Model):
    dm_repo_annual_id = db.Column(db.BigInteger, primary_key=True)
    repo_id = db.Column(db.BigInteger, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String(), server_default='NULL')
    year = db.Column(db.SmallInteger, nullable=False)
    added = db.Column(db.BigInteger, nullable=False)
    removed = db.Column(db.BigInteger, nullable=False)
    whitespace = db.Column(db.BigInteger, nullable=False)
    files = db.Column(db.BigInteger, nullable=False)
    patches = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'dm_repo_annual'
    __table_args__ = (
        db.Index("repo_id,affiliation_copy_1", repo_id, affiliation),
        db.Index("repo_id,email_copy_1", repo_id, email),
        {"schema": "augur_data"}
    )


class DmRepoGroupAnnual(db.Model):
    dm_repo_group_annual_id = db.Column(db.BigInteger, primary_key=True)
    repo_group_id = db.Column(db.BigInteger, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String(), server_default='NULL')
    year = db.Column(db.SmallInteger, nullable=False)
    added = db.Column(db.BigInteger, nullable=False)
    removed = db.Column(db.BigInteger, nullable=False)
    whitespace = db.Column(db.BigInteger, nullable=False)
    files = db.Column(db.BigInteger, nullable=False)
    patches = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'dm_repo_group_annual'
    __table_args__ = (
        db.Index("projects_id,affiliation_copy_1", repo_group_id, affiliation),
        db.Index("projects_id,email_copy_1", repo_group_id, email),
        {"schema": "augur_data"}
    )


class DmRepoGroupMonthly(db.Model):
    dm_repo_group_monthly_id = db.Column(db.BigInteger, primary_key=True)
    repo_group_id = db.Column(db.BigInteger, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String(), server_default='NULL')
    month = db.Column(db.SmallInteger, nullable=False)
    year = db.Column(db.SmallInteger, nullable=False)
    added = db.Column(db.BigInteger, nullable=False)
    removed = db.Column(db.BigInteger, nullable=False)
    whitespace = db.Column(db.BigInteger, nullable=False)
    files = db.Column(db.BigInteger, nullable=False)
    patches = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'dm_repo_group_monthly'
    __table_args__ = (
        db.Index("projects_id,affiliation_copy_2", repo_group_id, affiliation),
        db.Index("projects_id,email_copy_2", repo_group_id, email),
        db.Index("projects_id,year,affiliation_copy_1",
                 repo_group_id, year, affiliation),
        db.Index("projects_id,year,email_copy_1", repo_group_id, year, email),
        {"schema": "augur_data"}
    )


class DmRepoGroupWeekly(db.Model):
    dm_repo_group_weekly_id = db.Column(db.BigInteger, primary_key=True)
    repo_group_id = db.Column(db.BigInteger, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String(), server_default='NULL')
    week = db.Column(db.SmallInteger, nullable=False)
    year = db.Column(db.SmallInteger, nullable=False)
    added = db.Column(db.BigInteger, nullable=False)
    removed = db.Column(db.BigInteger, nullable=False)
    whitespace = db.Column(db.BigInteger, nullable=False)
    files = db.Column(db.BigInteger, nullable=False)
    patches = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'dm_repo_group_weekly'
    __table_args__ = (
        db.Index("projects_id,affiliation", repo_group_id, affiliation),
        db.Index("projects_id,email", repo_group_id, email),
        db.Index("projects_id,year,affiliation",
                 repo_group_id, year, affiliation),
        db.Index("projects_id,year,email", repo_group_id, year, email),
        {"schema": "augur_data"}
    )


class DmRepoMonthly(db.Model):
    dm_repo_monthly_id = db.Column(db.BigInteger, primary_key=True)
    repo_id = db.Column(db.BigInteger, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String(), server_default='NULL')
    month = db.Column(db.SmallInteger, nullable=False)
    year = db.Column(db.SmallInteger, nullable=False)
    added = db.Column(db.BigInteger, nullable=False)
    removed = db.Column(db.BigInteger, nullable=False)
    whitespace = db.Column(db.BigInteger, nullable=False)
    files = db.Column(db.BigInteger, nullable=False)
    patches = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'dm_repo_monthly'
    __table_args__ = (
        db.Index("repo_id,affiliation_copy_2", repo_id, affiliation),
        db.Index("repo_id,email_copy_2", repo_id, email),
        db.Index("repo_id,year,affiliation_copy_1",
                 repo_id, year, affiliation),
        db.Index("repo_id,year,email_copy_1", repo_id, year, email),
        {"schema": "augur_data"}
    )


class DmRepoWeekly(db.Model):
    dm_repo_weekly_id = db.Column(db.BigInteger, primary_key=True)
    repo_id = db.Column(db.BigInteger, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String(), server_default='NULL')
    week = db.Column(db.SmallInteger, nullable=False)
    year = db.Column(db.SmallInteger, nullable=False)
    added = db.Column(db.BigInteger, nullable=False)
    removed = db.Column(db.BigInteger, nullable=False)
    whitespace = db.Column(db.BigInteger, nullable=False)
    files = db.Column(db.BigInteger, nullable=False)
    patches = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'dm_repo_weekly'
    __table_args__ = (
        db.Index("repo_id,affiliation", repo_id, affiliation),
        db.Index("repo_id,email", repo_id, email),
        db.Index("repo_id,year,affiliation", repo_id, year, affiliation),
        db.Index("repo_id,year,email", repo_id, year, email),
        {"schema": "augur_data"}
    )


class Exclude(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    projects_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(), server_default='NULL')
    domain = db.Column(db.String(), server_default='NULL')

    __tablename__ = 'exclude'
    __table_args__ = (
        {"schema": "augur_data"}
    )


# TODO: Add relationship for repo_id: I don't think the repo_id should be in this table, I think that behavior can be obtained by getting all the issues for a repo then all the issue assignees for those issues
# TODO: Add relationship for cntrb_id
class IssueAssignees(db.Model):
    issue_assignee_id = db.Column(
        db.BigInteger, primary_key=True)
    issue_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.contributors.cntrb_id', name='fk_issue_assignees_contributors_1'))
    issue_assignee_src_id = db.Column(
        db.BigInteger, comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.")
    issue_assignee_src_node = db.Column(db.String(
    ), comment="This character based identifier comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'issue_assignees'
    __table_args__ = (

        UniqueConstraint('issue_id', 'repo_id', 'issue_assignee_src_id', name='unique-assignee-key'),
        ForeignKeyConstraint([issue_id, repo_id],
                            ["augur_data.issues.issue_id", 
                            "augur_data.issues.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),
        db.Index("issue-cntrb-assign-idx-1", cntrb_id),
        {"schema": "augur_data"}
    )

# TODO: Add relationship for repo_id: I don't think the repo_id should be in this table, I think that behavior can be obtained by getting all the issues for a repo then all the issue assignees for those issues
# TODO: Add relationship for cntrb_id


class IssueEvents(db.Model):
    event_id = db.Column(db.BigInteger, primary_key=True)
    issue_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                         name='fk_issue_events_contributors_1', ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    action = db.Column(db.String(), nullable=False)
    action_commit_hash = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP(), nullable=False,
                           server_default=func.current_timestamp())
    node_id = db.Column(db.String(), comment="This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.")
    node_url = db.Column(db.String())
    issue_event_src_id = db.Column(
        db.BigInteger, comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())
    platform_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.platform.pltfrm_id',
                            name='fk_issue_event_platform_ide', ondelete="RESTRICT", onupdate="CASCADE"))

    __tablename__ = 'issue_events'
    __table_args__ = (

        # contstraint to determine whether to insert or not
        UniqueConstraint('repo_id', 'issue_event_src_id',
                         name='unique_event_id_key'),

        ForeignKeyConstraint([issue_id, repo_id],
                            ["augur_data.issues.issue_id", 
                            "augur_data.issues.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),

        db.Index("issue-cntrb-idx2", issue_event_src_id),
        db.Index("issue_events_ibfk_1", issue_id),
        db.Index("issue_events_ibfk_2", cntrb_id),
        {"schema": "augur_data"}
    )

# TODO: Add relationship for repo_id: I don't think the repo_id should be in this table, I think that behavior can be obtained by getting all the issues for a repo then all the issue assignees for those issues


class IssueLabels(db.Model):
    issue_label_id = db.Column(db.BigInteger, primary_key=True)
    issue_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    label_text = db.Column(db.String())
    label_description = db.Column(db.String())
    label_color = db.Column(db.String())
    label_src_id = db.Column(
        db.BigInteger, comment="This character based identifier (node) comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API JSON subsection for issues.")
    label_src_node_id = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'issue_labels'
    __table_args__ = (
        # insert on
        UniqueConstraint('repo_id', 'issue_id', 'label_src_id', name='unique_issue_label'),

        ForeignKeyConstraint([issue_id, repo_id],
                            ["augur_data.issues.issue_id", 
                            "augur_data.issues.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),

        {"schema": "augur_data"}
    )

# TODO: Add replationship: for repo_id


class IssueMessageRef(db.Model):
    issue_msg_ref_id = db.Column(db.BigInteger, primary_key=True)
    issue_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_issue_message_ref_message_1',
                       ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    issue_msg_ref_src_node_id = db.Column(db.String(
    ), comment="This character based identifier comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API")
    issue_msg_ref_src_comment_id = db.Column(
        db.BigInteger, comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    message = relationship("Message", back_populates="issue")
    issue = relationship("Issues", back_populates="msg_ref")

    __tablename__ = 'issue_message_ref'
    __table_args__ = (

        # insert on
        UniqueConstraint('msg_id', 'repo_id', name='repo-issue'),

        ForeignKeyConstraint([issue_id, repo_id],
                            ["augur_data.issues.issue_id", 
                            "augur_data.issues.repo_id"], ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True),

        {"schema": "augur_data"}
    )

# TODO: Add relationship for cntrb_id
# should repo_id be allowed to be NULL?


class Issues(db.Model):
    issue_id = db.Column(db.BigInteger, primary_key=True)
    repo_id = db.Column(db.BigInteger,  db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_issues_repo', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    reporter_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                            name='fk_issues_contributors_2'), comment="The ID of the person who opened the issue. ")
    pull_request = db.Column(db.BigInteger)
    pull_request_id = db.Column(db.BigInteger)
    created_at = db.Column(db.TIMESTAMP())
    issue_title = db.Column(db.String())
    issue_body = db.Column(db.String())
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                         name='fk_issues_contributors_1'), comment="The ID of the person who closed the issue. ")
    comment_count = db.Column(db.BigInteger)
    updated_at = db.Column(db.TIMESTAMP())
    closed_at = db.Column(db.TIMESTAMP())
    due_on = db.Column(db.TIMESTAMP())
    repository_url = db.Column(db.String())
    issue_url = db.Column(db.String())
    labels_url = db.Column(db.String())
    comments_url = db.Column(db.String())
    events_url = db.Column(db.String())
    html_url = db.Column(db.String())
    issue_state = db.Column(db.String())
    issue_node_id = db.Column(db.String())
    gh_issue_number = db.Column(db.BigInteger)
    gh_issue_id = db.Column(db.BigInteger)
    gh_user_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    assignees = relationship("IssueAssignees")
    events = relationship("IssueEvents")
    labels = relationship("IssueLabels")

    msg_ref = relationship("IssueMessageRef", back_populates="issue")

    def get_messages(self):

        messages = []
        for msg_ref in self.msg_ref:
            messages.append(msg_ref.message)

        return messages

    __tablename__ = 'issues'
    __table_args__ = (

        db.Index("issue-cntrb-dix2", cntrb_id),
        db.Index("issues_ibfk_1", repo_id),
        db.Index("issues_ibfk_2", reporter_id),
        db.Index("issues_ibfk_4", pull_request_id),
        UniqueConstraint('issue_url', name='issue-unique'),
        {"schema": "augur_data"}
    )


# TODO: Should latest_release_timestamp be a timestamp
class Libraries(db.Model):
    library_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_libraries_repo_1'))
    platform = db.Column(db.String())
    name = db.Column(db.String())
    created_timestamp = db.Column(db.TIMESTAMP())
    updated_timestamp = db.Column(db.TIMESTAMP())
    library_description = db.Column(db.String())
    keywords = db.Column(db.String())
    library_homepage = db.Column(db.String())
    license = db.Column(db.String())
    version_count = db.Column(db.Integer)
    latest_release_timestamp = db.Column(db.String())
    latest_release_number = db.Column(db.String())
    package_manager_id = db.Column(db.String())
    dependency_count = db.Column(db.Integer)
    dependent_library_count = db.Column(db.Integer)
    primary_language = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    library_dependencies = relationship("LibraryDependecies")

    # TODO: Should this be a one to one relationship with library version (this it what I defined it as)?
    library_version = relationship("LibraryVersion", back_populates="library")

    __tablename__ = 'libraries'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class LibraryDependecies(db.Model):
    lib_dependency_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    library_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.libraries.library_id', name='fk_library_dependencies_libraries_1'))
    manifest_platform = db.Column(db.String())
    manifest_filepath = db.Column(db.String())
    manifest_kind = db.Column(db.String())
    repo_id_branch = db.Column(db.String(), nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'library_dependencies'
    __table_args__ = (
        db.Index("REPO_DEP", library_id),
        {"schema": "augur_data"}
    )


class LibraryVersion(db.Model):
    library_version_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    library_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.libraries.library_id', name='fk_library_version_libraries_1'))
    library_platform = db.Column(db.String())
    version_number = db.Column(db.String())
    version_release_date = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    library = relationship("Libraries", back_populates="library_version")

    __tablename__ = 'library_version'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class LstmAnomalyModels(db.Model):
    model_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    model_name = db.Column(db.String())
    model_description = db.Column(db.String())
    look_back_days = db.Column(db.BigInteger)
    training_days = db.Column(db.BigInteger)
    batch_size = db.Column(db.BigInteger)
    metric = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    # TODO: Should this be a one to one relationship?
    model_result = relationship("LstmAnomalyResults")

    __tablename__ = 'lstm_anomaly_models'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class LstmAnomalyResults(db.Model):
    result_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_lstm_anomaly_results_repo_1'))
    repo_category = db.Column(db.String())
    model_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.lstm_anomaly_models.model_id', name='fk_lstm_anomaly_results_lstm_anomaly_models_1'))
    metric = db.Column(db.String())
    contamination_factor = db.Column(db.Float())
    mean_absolute_error = db.Column(db.Float())
    remarks = db.Column(db.String())
    metric_field = db.Column(db.String(
    ), comment="This is a listing of all of the endpoint fields included in the generation of the metric. Sometimes there is one, sometimes there is more than one. This will list them all. ")
    mean_absolute_actual_value = db.Column(db.Float())
    mean_absolute_prediction_value = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'lstm_anomaly_results'
    __table_args__ = (
        {"schema": "augur_data"}
    )

# TODO: I don't think that repo_id needs to be included because this behavior could be achieved by Repo.ParentObj.msg_ref.message (ParentObj is things such as prs or issues)
# TODO: Add relationship to repo group list serve table


class Message(db.Model):
    msg_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    rgls_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo_groups_list_serve.rgls_id',
                        name='fk_message_repo_groups_list_serve_1', ondelete="CASCADE", onupdate="CASCADE"))
    platform_msg_id = db.Column(db.BigInteger)
    platform_node_id = db.Column(db.String())
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_message_repoid',
                        ondelete="CASCADE", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_message_contributors_1',
                         ondelete="CASCADE", onupdate="CASCADE"), comment="Not populated for mailing lists. Populated for GitHub issues. ")
    msg_text = db.Column(db.String())
    msg_timestamp = db.Column(db.TIMESTAMP())
    msg_sender_email = db.Column(db.String())
    msg_header = db.Column(db.String())
    pltfrm_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.platform.pltfrm_id',
                          name='fk_message_platform_1', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    # Used this thread to determine how to do one to many relationship with an extra middle table: https://stackoverflow.com/questions/35795717/flask-sqlalchemy-many-to-many-relationship-with-extra-field
    commit = relationship("CommitCommentRef", back_populates="message")
    issue = relationship("IssueMessageRef", back_populates="message")
    pull_request = relationship(
        "PullRequestMessageRef", back_populates="message")
    pr_review = relationship(
        "PullRequestReviewMessageRef", back_populates="message")

    analysis = relationship("MessageAnalysis", back_populates="message")
    sentiment = relationship("MessageSentiment", back_populates="message")

    __tablename__ = 'message'
    __table_args__ = (
        UniqueConstraint('platform_msg_id', name='gh-message'),
        db.Index("messagegrouper", msg_id, rgls_id, unique=True),
        db.Index("msg-cntrb-id-idx", cntrb_id),
        db.Index("platformgrouper", msg_id, pltfrm_id),
        {"schema": "augur_data"}
    )


class MessageAnalysis(db.Model):
    msg_analysis_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    msg_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.message.msg_id', name='fk_message_analysis_message_1'))
    worker_run_id = db.Column(
        db.BigInteger, comment="This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ")
    sentiment_score = db.Column(db.Float(
    ), comment="A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ")
    reconstruction_error = db.Column(db.Float(
    ), comment="Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.")
    novelty_flag = db.Column(db.Boolean(), comment="This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ")
    feedback_flag = db.Column(db.Boolean(
    ), comment="This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    message = relationship("Message", back_populates="analysis")

    __tablename__ = 'message_analysis'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class MessageAnalysisSummary(db.Model):
    msg_summary_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_message_analysis_summary_repo_1'))
    worker_run_id = db.Column(db.BigInteger)
    positive_ratio = db.Column(db.Float())
    negative_ratio = db.Column(db.Float())
    novel_count = db.Column(db.BigInteger)
    period = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    # TODO: Ensure that this is a one to one relationship
    repo = relationship("Repo", back_populates="msg_analysis_summary")

    __tablename__ = 'message_analysis_summary'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class MessageSentiment(db.Model):
    msg_analysis_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    msg_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.message.msg_id', name='fk_message_sentiment_message_1'))
    worker_run_id = db.Column(
        db.BigInteger, comment="This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ")
    sentiment_score = db.Column(db.Float(
    ), comment="A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ")
    reconstruction_error = db.Column(db.Float(
    ), comment="Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.")
    novelty_flag = db.Column(db.Boolean(), comment="This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ")
    feedback_flag = db.Column(db.Boolean(
    ), comment="This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    message = relationship("Message", back_populates="sentiment")

    __tablename__ = 'message_sentiment'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class MessageSentimentSummary(db.Model):
    msg_summary_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_message_sentiment_summary_repo_1'))
    worker_run_id = db.Column(db.BigInteger, comment='This value should reflect the worker_run_id for the messages summarized in the table. There is not a relation between these two tables for that purpose because its not *really*, relationaly a concept unless we create a third table for "worker_run_id", which we determined was unnecessarily complex. ')
    positive_ratio = db.Column(db.Float())
    negative_ratio = db.Column(db.Float())
    novel_count = db.Column(
        db.BigInteger, comment="The number of messages identified as novel during the analyzed period")
    period = db.Column(db.TIMESTAMP(), comment="The whole timeline is divided into periods based on the definition of time period for analysis, which is user specified. Timestamp of the first period to look at, until the end of messages at the data of execution. ")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    repo = relationship("Repo", back_populates="msg_sentiment_summary")

    __tablename__ = 'message_sentiment_summary'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": "In a relationally perfect world, we would have a table called “message_sentiment_run” the incremented the “worker_run_id” for both message_sentiment and message_sentiment_summary. For now, we decided this was overkill. "}
    )


class Platform(db.Model):
    pltfrm_id = db.Column(db.BigInteger, nullable=False)
    pltfrm_name = db.Column(db.String())
    pltfrm_version = db.Column(db.String())
    pltfrm_release_date = db.Column(db.Date)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    pr_reviews = relationship("PullRequestReviews")

    __tablename__ = 'platform'
    __table_args__ = (
        PrimaryKeyConstraint('pltfrm_id', name='theplat'),
        db.Index("plat", pltfrm_id, unique=True),
        {"schema": "augur_data"}
    )


class PullRequestAnalysis(db.Model):
    pull_request_analysis_id = db.Column(
        db.BigInteger, primary_key=True)
    pull_request_id = db.Column(db.BigInteger, comment="It would be better if the pull request worker is run first to fetch the latest PRs before analyzing")
    repo_id = db.Column(db.BigInteger)
    merge_probability = db.Column(db.Numeric(
        precision=256, scale=250), comment="Indicates the probability of the PR being merged")
    mechanism = db.Column(db.String(
    ), comment="the ML model used for prediction (It is XGBoost Classifier at present)")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

    pull_request = relationship("PullRequests", back_populates="analysis")

    __tablename__ = 'pull_request_analysis'
    __table_args__ = (
        UniqueConstraint('repo_id', 'pull_request_id', name='pr-analysis-unique'),
        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),

        db.Index("pr_anal_idx", pull_request_id),
        db.Index("probability_idx", merge_probability.desc().nullslast()),
        {"schema": "augur_data"}
    )

# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.assignees
# TODO: Add relationship for cntrb_id


class PullRequestAssignees(db.Model):
    pr_assignee_map_id = db.Column(
        db.BigInteger, primary_key=True)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    contrib_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.contributors.cntrb_id', name='fk_pull_request_assignees_contributors_1'))
    pr_assignee_src_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'pull_request_assignees'
    __table_args__ = (
        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"], ondelete="RESTRICT", onupdate="CASCADE"),

        db.Index("pr_meta_cntrb-idx", contrib_id),
        UniqueConstraint('repo_id', 'pull_request_id', 'pr_assignee_src_id', name='pr-assignee-unique'),
        {"schema": "augur_data"}
    )


# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.commits
# TODO: Add relationship for cntrb_id
class PullRequestCommits(db.Model):
    pr_cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    pr_cmt_sha = db.Column(db.String(), comment="This is the commit SHA for a pull request commit. If the PR is not to the master branch of the main repository (or, in rare cases, from it), then you will NOT find a corresponding commit SHA in the commit table. (see table comment for further explanation). ")
    pr_cmt_node_id = db.Column(db.String())
    pr_cmt_message = db.Column(db.String())
    pr_cmt_comments_url = db.Column(db.String())
    pr_cmt_author_cntrb_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.contributors.cntrb_id', name='fk_pr_commit_cntrb_id', ondelete="CASCADE", onupdate="CASCADE"))
    pr_cmt_timestamp = db.Column(db.TIMESTAMP())
    pr_cmt_author_email = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'pull_request_commits'
    __table_args__ = (
        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),

        UniqueConstraint('pull_request_id', 'repo_id',
                         'pr_cmt_sha', name='pr_commit_nk'),
        {"schema": "augur_data",
         "comment": "Pull request commits are an enumeration of each commit associated with a pull request. \nNot all pull requests are from a branch or fork into master. \nThe commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).\nTherefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. \nIn cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. "}
    )

# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.events
# TODO: Add relationship for cntrb_id


class PullRequestEvents(db.Model):
    pr_event_id = db.Column(db.BigInteger, primary_key=True)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.contributors.cntrb_id', name='fk_pull_request_events_contributors_1'), nullable=False)
    action = db.Column(db.String(), nullable=False)
    action_commit_hash = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP(), nullable=False,
                           server_default=func.current_timestamp())
    issue_event_src_id = db.Column(
        db.BigInteger, comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API")
    node_id = db.Column(db.String(), comment="This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.")
    node_url = db.Column(db.String())
    platform_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.platform.pltfrm_id', name='fkpr_platform',
                            ondelete="RESTRICT", onupdate="RESTRICT", initially="DEFERRED", deferrable=True), server_default=text('25150'))
    pr_platform_event_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'pull_request_events'
    __table_args__ = (
        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),

        # 
        UniqueConstraint('repo_id', 'issue_event_src_id',
                         name='unique-pr-event-id'),
        db.Index("pr_events_ibfk_1", pull_request_id),
        db.Index("pr_events_ibfk_2", cntrb_id),
        {"schema": "augur_data"}
    )


# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.files
class PullRequestFiles(db.Model):
    pr_file_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    pr_file_additions = db.Column(db.BigInteger)
    pr_file_deletions = db.Column(db.BigInteger)
    pr_file_path = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'pull_request_files'
    __table_args__ = (

        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"]),

        # TODO: Confirm: Values to determine if insert needed
        UniqueConstraint('pull_request_id', 'repo_id',
                         'pr_file_path', name='prfiles_unique'),
        {"schema": "augur_data",
         "comment": "Pull request commits are an enumeration of each commit associated with a pull request. \nNot all pull requests are from a branch or fork into master. \nThe commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).\nTherefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. \nIn cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. "}
    )

# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.labels


class PullRequestLabels(db.Model):
    pr_label_id = db.Column(db.BigInteger, primary_key=True)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    pr_src_id = db.Column(db.BigInteger)
    pr_src_node_id = db.Column(db.String())
    pr_src_url = db.Column(db.String())
    pr_src_description = db.Column(db.String())
    pr_src_color = db.Column(db.String())
    pr_src_default_bool = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'pull_request_labels'
    __table_args__ = (

        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),

        # TODO: Confirm: Values to determine if insert needed
        UniqueConstraint('repo_id', 'pull_request_id', 'pr_src_id',
                         name='unique-pr-src-label-id'),
        {"schema": "augur_data"}
    )

# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.msg_ref


class PullRequestMessageRef(db.Model):
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger, primary_key=True)
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_pull_request_message_ref_message_1',
                       ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True), primary_key=True)
    pr_message_ref_src_comment_id = db.Column(db.BigInteger)
    pr_message_ref_src_node_id = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())
    pr_issue_url = db.Column(db.String())

    message = relationship("Message", back_populates="pull_request")
    pull_request = relationship("PullRequests", back_populates="msg_ref")

    __tablename__ = 'pull_request_message_ref'
    __table_args__ = (

        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),

        # TODO: Confirm: Values to determine if insert needed
        UniqueConstraint('pr_message_ref_src_comment_id',
                         'tool_source', name='pr-comment-nk'),
        {"schema": "augur_data"}
    )

# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.meta_data


class PullRequestMeta(db.Model):
    pr_repo_meta_id = db.Column(
        db.BigInteger, primary_key=True)
    pull_request_id = db.Column(db.BigInteger, primary_key=True)
    repo_id = db.Column(db.BigInteger, primary_key=True)
    pr_head_or_base = db.Column(db.String(
    ), comment="Each pull request should have one and only one head record; and one and only one base record. ")
    pr_src_meta_label = db.Column(db.String())
    pr_src_meta_ref = db.Column(db.String())
    pr_sha = db.Column(db.String())
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.contributors.cntrb_id', name='fk_pull_request_meta_contributors_2'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'pull_request_meta'
    __table_args__ = (
        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"]),

        db.Index("pr_meta-cntrbid-idx", cntrb_id),
        UniqueConstraint('pull_request_id', 'pr_head_or_base', 'pr_sha', name='pr-meta-unique'),
        {"schema": "augur_data",
         "comment": 'Pull requests contain referencing metadata.  There are a few columns that are discrete. There are also head and base designations for the repo on each side of the pull request. Similar functions exist in GitLab, though the language here is based on GitHub. The JSON Being adapted to as of the development of this schema is here:      "base": {       "label": "chaoss:dev",       "ref": "dev",       "sha": "dc6c6f3947f7dc84ecba3d8bda641ef786e7027d",       "user": {         "login": "chaoss",         "id": 29740296,         "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",         "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",         "gravatar_id": "",         "url": "https://api.github.com/users/chaoss",         "html_url": "https://github.com/chaoss",         "followers_url": "https://api.github.com/users/chaoss/followers",         "following_url": "https://api.github.com/users/chaoss/following{/other_user}",         "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",         "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",         "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",         "organizations_url": "https://api.github.com/users/chaoss/orgs",         "repos_url": "https://api.github.com/users/chaoss/repos",         "events_url": "https://api.github.com/users/chaoss/events{/privacy}",         "received_events_url": "https://api.github.com/users/chaoss/received_events",         "type": "Organization",         "site_admin": false       },       "repo": {         "id": 78134122,         "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",         "name": "augur",         "full_name": "chaoss/augur",         "private": false,         "owner": {           "login": "chaoss",           "id": 29740296,           "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",           "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",           "gravatar_id": "",           "url": "https://api.github.com/users/chaoss",           "html_url": "https://github.com/chaoss",           "followers_url": "https://api.github.com/users/chaoss/followers",           "following_url": "https://api.github.com/users/chaoss/following{/other_user}",           "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",           "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",           "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",           "organizations_url": "https://api.github.com/users/chaoss/orgs",           "repos_url": "https://api.github.com/users/chaoss/repos",           "events_url": "https://api.github.com/users/chaoss/events{/privacy}",           "received_events_url": "https://api.github.com/users/chaoss/received_events",           "type": "Organization",           "site_admin": false         }, '}
    )

# TODO: Don't know enough about table structure to create relationship


# class PullRequestRepo(db.Model):
#     pr_repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
#     pr_repo_meta_id = db.Column(db.BigInteger)
#     pull_request_id = db.Column(db.BigInteger)
#     pr_repo_head_or_base = db.Column(db.String(
#     ), comment="For ease of validation checking, we should determine if the repository referenced is the head or base of the pull request. Each pull request should have one and only one of these, which is not enforcable easily in the database.")
#     pr_src_repo_id = db.Column(db.BigInteger)
#     pr_src_node_id = db.Column(db.String())
#     pr_repo_name = db.Column(db.String())
#     pr_repo_full_name = db.Column(db.String())
#     pr_repo_private_bool = db.Column(db.Boolean())
#     pr_cntrb_id = db.Column(db.BigInteger, db.ForeignKey(
#         'augur_data.contributors.cntrb_id', name='fk_pull_request_repo_contributors_1'))
#     tool_source = db.Column(db.String())
#     tool_version = db.Column(db.String())
#     data_source = db.Column(db.String())
#     data_collection_date = db.Column(
#         db.TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = 'pull_request_repo'
#     __table_args__ = (
#         ForeignKeyConstraint([pull_request_id, pr_repo_meta_id],
#                             ["augur_data.pull_request_meta.pull_request_id", 
#                             "augur_data.pull_request_meta.pr_repo_meta_id"], ondelete="CASCADE", onupdate="CASCADE"),
#         db.Index("pr-cntrb-idx-repo", pr_cntrb_id),
#         {"schema": "augur_data",
#          "comment": "This table is for storing information about forks that exist as part of a pull request. Generally we do not want to track these like ordinary repositories. "}
#     )

# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.reviews.msg_ref


class PullRequestReviewMessageRef(db.Model):
    pr_review_id = db.Column(db.BigInteger, primary_key=True)
    pull_request_id = db.Column(db.BigInteger, primary_key=True)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_review_repo',
                        ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True), primary_key=True)
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_pull_request_review_message_ref_message_1',
                       ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True), primary_key=True)
    pr_review_msg_url = db.Column(db.String())
    pr_review_src_id = db.Column(db.BigInteger)
    pr_review_msg_src_id = db.Column(db.BigInteger)
    pr_review_msg_node_id = db.Column(db.String())
    pr_review_msg_diff_hunk = db.Column(db.String())
    pr_review_msg_path = db.Column(db.String())
    pr_review_msg_position = db.Column(db.BigInteger)
    pr_review_msg_original_position = db.Column(db.BigInteger)
    pr_review_msg_commit_id = db.Column(db.String())
    pr_review_msg_original_commit_id = db.Column(db.String())
    pr_review_msg_updated_at = db.Column(db.TIMESTAMP())
    pr_review_msg_html_url = db.Column(db.String())
    pr_url = db.Column(db.String())
    pr_review_msg_author_association = db.Column(db.String())
    pr_review_msg_start_line = db.Column(db.BigInteger)
    pr_review_msg_original_start_line = db.Column(db.BigInteger)
    pr_review_msg_start_side = db.Column(db.String())
    pr_review_msg_line = db.Column(db.BigInteger)
    pr_review_msg_original_line = db.Column(db.BigInteger)
    pr_review_msg_side = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    message = relationship("Message", back_populates="pr_review")
    pr_review = relationship("PullRequestReviews", back_populates="msg_ref")

    __tablename__ = 'pull_request_review_message_ref'
    __table_args__ = (
        ForeignKeyConstraint([pull_request_id, repo_id],
                    ["augur_data.pull_requests.pull_request_id", 
                    "augur_data.pull_requests.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),

        UniqueConstraint('pr_review_msg_src_id',
                         'tool_source', name='pr-review-nk'),
        {"schema": "augur_data"}
    )

# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.reviewers
# TODO: Add cntrb_id relationship (don't understand table well enough)


class PullRequestReviewers(db.Model):
    pr_reviewer_map_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger)
    pr_source_id = db.Column(
        db.BigInteger, comment="The platform ID for the pull/merge request. Used as part of the natural key, along with pr_reviewer_src_id in this table. ")
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                         name='fk_pull_request_reviewers_contributors_1', ondelete="CASCADE", onupdate="CASCADE"))
    pr_reviewer_src_id = db.Column(
        db.BigInteger, comment="The platform ID for the pull/merge request reviewer. Used as part of the natural key, along with pr_source_id in this table. ")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'pull_request_reviewers'
    __table_args__ = (
        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),

        UniqueConstraint('pr_source_id', 'pr_reviewer_src_id',
                         name='unique_pr_src_reviewer_key', initially="DEFERRED", deferrable=True),
        UniqueConstraint('pull_request_id', 'pr_reviewer_src_id', name='pr-reviewers-unique'),
        db.Index("pr-reviewers-cntrb-idx1", cntrb_id),
        {"schema": "augur_data"}
    )

# TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.reviews
# TODO: Add relationship for cntrb_id


class PullRequestReviews(db.Model):
    pr_review_id = db.Column(db.BigInteger, primary_key=True)
    pull_request_id = db.Column(db.BigInteger, primary_key=True)
    repo_id = db.Column(db.BigInteger, primary_key=True)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                         name='fk_pull_request_reviews_contributors_1', ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    pr_review_author_association = db.Column(db.String())
    pr_review_state = db.Column(db.String())
    pr_review_body = db.Column(db.String())
    pr_review_submitted_at = db.Column(db.TIMESTAMP())
    pr_review_src_id = db.Column(db.BigInteger)
    pr_review_node_id = db.Column(db.String())
    pr_review_html_url = db.Column(db.String())
    pr_review_pull_request_url = db.Column(db.String())
    pr_review_commit_id = db.Column(db.String())
    platform_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.platform.pltfrm_id', name='fk-review-platform',
                            ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True), server_default=text('25150'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    msg_ref = relationship("PullRequestReviewMessageRef",
                           back_populates="pr_review")

    def get_messages(self):

        messages = []
        for msg_ref in self.msg_ref:
            messages.append(msg_ref.message)

        return messages

    __tablename__ = 'pull_request_reviews'
    __table_args__ = (
        ForeignKeyConstraint([pull_request_id, repo_id],
                            ["augur_data.pull_requests.pull_request_id", 
                            "augur_data.pull_requests.repo_id"], ondelete="CASCADE", onupdate="CASCADE"),
        UniqueConstraint('pr_review_src_id', 'tool_source',
                         name='sourcepr-review-id'),
        {"schema": "augur_data"}
    )


class PullRequestTeams(db.Model):
    pr_team_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    pr_src_team_id = db.Column(db.BigInteger)
    pr_src_team_node = db.Column(db.String())
    pr_src_team_url = db.Column(db.String())
    pr_team_name = db.Column(db.String())
    pr_team_slug = db.Column(db.String())
    pr_team_description = db.Column(db.String())
    pr_team_privacy = db.Column(db.String())
    pr_team_permission = db.Column(db.String())
    pr_team_src_members_url = db.Column(db.String())
    pr_team_src_repositories_url = db.Column(db.String())
    pr_team_parent_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'pull_request_teams'
    __table_args__ = (
        ForeignKeyConstraint([pull_request_id, repo_id],
                    ["augur_data.pull_requests.pull_request_id", 
                    "augur_data.pull_requests.repo_id"]),
        {"schema": "augur_data"}
    )


class PullRequests(db.Model):

    pull_request_id = db.Column(
        db.BigInteger, primary_key=True)
    repo_id = db.Column(db.BigInteger, 
                db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_requests_repo_1', ondelete="CASCADE", onupdate="CASCADE"), primary_key=True)
    pr_url = db.Column(db.String())
    pr_src_id = db.Column(
        db.BigInteger, comment="The pr_src_id is unique across all of github.")
    pr_src_node_id = db.Column(db.String())
    pr_html_url = db.Column(db.String())
    pr_diff_url = db.Column(db.String())
    pr_patch_url = db.Column(db.String())
    pr_issue_url = db.Column(db.String())
    pr_augur_issue_id = db.Column(
        db.BigInteger, comment="This is to link to the augur stored related issue")
    pr_src_number = db.Column(
        db.BigInteger, comment="The pr_src_number is unique within a repository.")
    pr_src_state = db.Column(db.String())
    pr_src_locked = db.Column(db.Boolean())
    pr_src_title = db.Column(db.String())
    pr_augur_contributor_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pr_contribs',
                                        ondelete="RESTRICT", onupdate="CASCADE"), comment="This is to link to the augur contributor record. ")
    pr_body = db.Column(db.Text())
    pr_created_at = db.Column(db.TIMESTAMP())
    pr_updated_at = db.Column(db.TIMESTAMP())
    pr_closed_at = db.Column(db.TIMESTAMP())
    pr_merged_at = db.Column(db.TIMESTAMP())
    pr_merge_commit_sha = db.Column(db.String())
    pr_teams = db.Column(
        db.BigInteger, comment="One to many with pull request teams. ")
    pr_milestone = db.Column(db.String())
    pr_commits_url = db.Column(db.String())
    pr_review_comments_url = db.Column(db.String())
    pr_review_comment_url = db.Column(db.String(
    ), comment="This is a field with limited utility. It does expose how to access a specific comment if needed with parameters. If the source changes URL structure, it may be useful")
    pr_comments_url = db.Column(db.String())
    pr_statuses_url = db.Column(db.String())
    pr_meta_head_id = db.Column(db.String(
    ), comment="The metadata for the head repo that links to the pull_request_meta table. ")
    pr_meta_base_id = db.Column(db.String(
    ), comment="The metadata for the base repo that links to the pull_request_meta table. ")
    pr_src_issue_url = db.Column(db.String())
    pr_src_comments_url = db.Column(db.String())
    pr_src_review_comments_url = db.Column(db.String())
    pr_src_commits_url = db.Column(db.String())
    pr_src_statuses_url = db.Column(db.String())
    pr_src_author_association = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())


    analysis = relationship("PullRequestAnalysis",
                            back_populates="pull_request")
    assignees = relationship("PullRequestAssignees")
    commits = relationship("PullRequestCommits")
    events = relationship("PullRequestEvents")
    files = relationship("PullRequestFiles")
    labels = relationship("PullRequestLabels")
    msg_ref = relationship("PullRequestMessageRef",
                           back_populates="pull_request")
    meta_data = relationship("PullRequestMeta")
    reviewers = relationship("PullRequestReviewers")
    reviews = relationship("PullRequestReviews")
    teams = relationship("PullRequestTeams")

    def get_messages(self):

        messages = []
        for msg_ref in self.msg_ref:
            messages.append(msg_ref.message)

        return messages

    __tablename__ = 'pull_requests'
    __table_args__ = (
        db.Index("id_node", pr_src_id.desc().nullsfirst(),
                 pr_src_node_id.desc().nullsfirst()),
        db.Index("pull_requests_idx_repo_id_data_datex",
                 repo_id, data_collection_date),
        UniqueConstraint('pr_url', name='pr-unique'),
        {"schema": "augur_data"}
    )


class Releases(db.Model):
    release_id = db.Column(
        db.CHAR(length=64), primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_releases_repo_1'), nullable=False)
    release_name = db.Column(db.String())
    release_description = db.Column(db.String())
    release_author = db.Column(db.String())
    release_created_at = db.Column(db.TIMESTAMP())
    release_published_at = db.Column(db.TIMESTAMP())
    release_updated_at = db.Column(db.TIMESTAMP())
    release_is_draft = db.Column(db.Boolean())
    release_is_prerelease = db.Column(db.Boolean())
    release_tag_name = db.Column(db.String())
    release_url = db.Column(db.String())
    tag_only = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'releases'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class Repo(db.Model):
    repo_id = db.Column(db.BigInteger, primary_key=True, autoincrement=False)
    repo_group_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo_groups.repo_group_id', name='fk_repo_repo_groups_1'), nullable=False)
    repo_git = db.Column(db.String(), nullable=False)
    repo_path = db.Column(db.String(), server_default='NULL')
    repo_name = db.Column(db.String(), server_default='NULL')
    repo_added = db.Column(db.TIMESTAMP(), nullable=False,
                           server_default=func.current_timestamp())
    repo_status = db.Column(db.String(), nullable=False, server_default='New')
    repo_type = db.Column(db.String(), server_default='', comment='This field is intended to indicate if the repository is the "main instance" of a repository in cases where implementations choose to add the same repository to more than one repository group. In cases where the repository group is of rg_type Github Organization then this repo_type should be "primary". In other cases the repo_type should probably be "user created". We made this a varchar in order to hold open the possibility that there are additional repo_types we have not thought about. ')
    url = db.Column(db.String())
    owner_id = db.Column(db.Integer)
    description = db.Column(db.String())
    primary_language = db.Column(db.String())
    created_at = db.Column(db.String())
    forked_from = db.Column(db.String())
    updated_at = db.Column(db.TIMESTAMP())
    repo_archived_date_collected = db.Column(db.TIMESTAMP(timezone=True))
    repo_archived = db.Column(db.Integer)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    commits = relationship("Commits")
    issues = relationship("Issues")
    pull_requests = relationship("PullRequests")
    libraries = relationship("Libraries")
    messages = relationship("Message")

    pr_assignees = relationship("PullRequestAssignees")
    pr_commits = relationship("PullRequestCommits")
    pr_events = relationship("PullRequestEvents")
    pr_files = relationship("PullRequestFiles")
    pr_labels = relationship("PullRequestLabels")
    pr_meta_data = relationship("PullRequestMeta")
    pr_reviews = relationship("PullRequestReviews")

    msg_analysis_summary = relationship(
        "MessageAnalysisSummary", back_populates="repo")
    msg_sentiment_summary = relationship(
        "MessageSentimentSummary", back_populates="repo")

    lstm_anomaly_results = relationship("LstmAnomalyResults")

    releases = relationship("Releases")
    badges = relationship("RepoBadging")
    cluster_messages = relationship("RepoClusterMessages")
    dependencies = relationship("RepoDependencies")
    deps_libyear = relationship("RepoDepsLibyear")
    deps_scorecard_id = relationship("RepoDepsScorecard")

    info = relationship("RepoInfo")
    insights = relationship("RepoInsights")
    insight_records = relationship("RepoInsightsRecords")

    labor = relationship("RepoLabor")
    meta_data = relationship("RepoMeta")
    sbom_scans = relationship("RepoSbomScans")
    stats = relationship("RepoStats")
    topic = relationship("RepoTopic")

    __tablename__ = 'repo'
    __table_args__ = (
        db.Index("forked", forked_from),
        db.Index("repo_idx_repo_id_repo_namex", repo_id, repo_name),
        db.Index("repogitindexrep", repo_git),

        db.Index("reponameindex", repo_name, postgresql_using='hash'),

        db.Index("reponameindexbtree", repo_name),
        db.Index("rggrouponrepoindex", repo_group_id),
        db.Index("therepo", repo_id, unique=True),
        {"schema": "augur_data",
         "comment": "This table is a combination of the columns in Facade’s repo table and GHTorrent’s projects table. "}
    )


class RepoBadging(db.Model):
    badge_collection_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_repo_badging_repo_1'))
    created_at = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())
    data = db.Column(JSONB())

    __tablename__ = 'repo_badging'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": 'This will be collected from the LF’s Badging API\nhttps://bestpractices.coreinfrastructure.org/projects.json?pq=https%3A%2F%2Fgithub.com%2Fchaoss%2Faugur\n'}
    )


class RepoClusterMessages(db.Model):
    msg_cluster_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_repo_cluster_messages_repo_1'))
    cluster_content = db.Column(db.Integer)
    cluster_mechanism = db.Column(db.Integer)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_cluster_messages'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class RepoDependencies(db.Model):
    repo_dependencies_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='repo_id'), comment="Forign key for repo id. ")
    dep_name = db.Column(
        db.String(), comment="Name of the dependancy found in project. ")
    dep_count = db.Column(
        db.Integer, comment="Number of times the dependancy was found. ")
    dep_language = db.Column(
        db.String(), comment="Language of the dependancy. ")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_dependencies'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": "Contains the dependencies for a repo."}
    )


# TODO: typo in field current_verion
class RepoDepsLibyear(db.Model):
    repo_deps_libyear_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='repo_id_copy_2'))
    name = db.Column(db.String())
    requirement = db.Column(db.String())
    type = db.Column(db.String())
    package_manager = db.Column(db.String())
    current_verion = db.Column(db.String())
    latest_version = db.Column(db.String())
    current_release_date = db.Column(db.String())
    latest_release_date = db.Column(db.String())
    libyear = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_deps_libyear'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class RepoDepsScorecard(db.Model):
    repo_deps_scorecard_id = db.Column(db.BigInteger, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='repo_id_copy_1'))
    name = db.Column(db.String())
    status = db.Column(db.String())
    score = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_deps_scorecard'
    __table_args__ = (
        PrimaryKeyConstraint('repo_deps_scorecard_id',
                             name='repo_deps_scorecard_pkey1'),
        {"schema": "augur_data"}
    )


class RepoGroupInsights(db.Model):
    rgi_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_group_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo_groups.repo_group_id', name='fk_repo_group_insights_repo_groups_1'))
    rgi_metric = db.Column(db.String())
    rgi_value = db.Column(db.String())
    cms_id = db.Column(db.BigInteger)
    rgi_fresh = db.Column(db.Boolean(), comment='false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ')
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    repo_group = relationship("RepoGroups")

    __tablename__ = 'repo_group_insights'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a REPOSITORY_GROUP and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. \n\nWorker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. '}
    )


class RepoGroups(db.Model):
    repo_group_id = db.Column(db.BigInteger, nullable=False)
    rg_name = db.Column(db.String(), nullable=False)
    rg_description = db.Column(db.String(), server_default='NULL')
    rg_website = db.Column(db.String(), server_default='NULL')
    rg_recache = db.Column(db.SmallInteger, server_default=text('1'))
    rg_last_modified = db.Column(
        db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())
    rg_type = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    repos = relationship("Repo")
    rg_list_serve = relationship("RepoGroupsListServe")

    __tablename__ = 'repo_groups'
    __table_args__ = (
        PrimaryKeyConstraint('repo_group_id', name='rgid'),
        db.Index("rgidm", repo_group_id, unique=True),
        db.Index("rgnameindex", rg_name),
        {"schema": "augur_data",
         "comment": "rg_type is intended to be either a GitHub Organization or a User Created Repo Group. "}
    )


class RepoGroupsListServe(db.Model):
    rgls_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_group_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo_groups.repo_group_id', name='fk_repo_groups_list_serve_repo_groups_1'), nullable=False)
    rgls_name = db.Column(db.String())
    rgls_description = db.Column(db.String())
    rgls_sponsor = db.Column(db.String())
    rgls_email = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_groups_list_serve'
    __table_args__ = (
        UniqueConstraint('rgls_id', 'repo_group_id', name='rglistserve'),
        db.Index("lister", rgls_id, repo_group_id, unique=True),
        {"schema": "augur_data"}
    )


class RepoInfo(db.Model):
    repo_info_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_repo_info_repo_1'), nullable=False)
    last_updated = db.Column(db.TIMESTAMP())
    issues_enabled = db.Column(db.String())
    open_issues = db.Column(db.Integer)
    pull_requests_enabled = db.Column(db.String())
    wiki_enabled = db.Column(db.String())
    pages_enabled = db.Column(db.String())
    fork_count = db.Column(db.Integer)
    default_branch = db.Column(db.String())
    watchers_count = db.Column(db.Integer)
    UUID = db.Column(db.Integer)
    license = db.Column(db.String())
    stars_count = db.Column(db.Integer)
    committers_count = db.Column(db.Integer)
    issue_contributors_count = db.Column(db.String())
    changelog_file = db.Column(db.String())
    contributing_file = db.Column(db.String())
    license_file = db.Column(db.String())
    code_of_conduct_file = db.Column(db.String())
    security_issue_file = db.Column(db.String())
    security_audit_file = db.Column(db.String())
    status = db.Column(db.String())
    keywords = db.Column(db.String())
    commit_count = db.Column(db.BigInteger)
    issues_count = db.Column(db.BigInteger)
    issues_closed = db.Column(db.BigInteger)
    pull_request_count = db.Column(db.BigInteger)
    pull_requests_open = db.Column(db.BigInteger)
    pull_requests_closed = db.Column(db.BigInteger)
    pull_requests_merged = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_info'
    __table_args__ = (
        # TODO: Their appears to be two of the same index in current database
        db.Index("repo_info_idx_repo_id_data_date_1x",
                 repo_id, data_collection_date),
        {"schema": "augur_data"}
    )


# TODO: Why is numeric defined without level or precision?
class RepoInsights(db.Model):
    ri_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_repo_insights_repo_1'))
    ri_metric = db.Column(db.String())
    ri_value = db.Column(db.String())
    ri_date = db.Column(db.TIMESTAMP())
    ri_fresh = db.Column(db.Boolean(), comment='false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ')
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())
    ri_score = db.Column(db.Numeric())
    ri_field = db.Column(db.String())
    ri_detection_method = db.Column(db.String())

    __tablename__ = 'repo_insights'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a repository and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. \n\nWorker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. '}
    )


class RepoInsightsRecords(db.Model):
    ri_id = db.Column(db.BigInteger, primary_key=True,
                      nullable=False, comment="Primary key. ")
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='repo_id_ref', ondelete="SET NULL",
                        onupdate="CASCADE"), comment="Refers to repo table primary key. Will have a foreign key")
    ri_metric = db.Column(db.String(), comment="The metric endpoint")
    ri_field = db.Column(
        db.String(), comment="The field in the metric endpoint")
    ri_value = db.Column(
        db.String(), comment="The value of the endpoint in ri_field")
    ri_date = db.Column(db.TIMESTAMP(
    ), comment="The date the insight is for; in other words, some anomaly occurred on this date. ")
    ri_score = db.Column(
        db.Float(), comment="A Score, derived from the algorithm used. ")
    ri_detection_method = db.Column(db.String(
    ), comment='A confidence interval or other expression of the type of threshold and the value of a threshold met in order for it to be "an insight". Example. "95% confidence interval". ')
    tool_source = db.Column(db.String(), comment="Standard Augur Metadata")
    tool_version = db.Column(db.String(), comment="Standard Augur Metadata")
    data_source = db.Column(db.String(), comment="Standard Augur Metadata")
    data_collection_date = db.Column(db.TIMESTAMP(
    ), server_default=func.current_timestamp(), comment="Standard Augur Metadata")

    __tablename__ = 'repo_insights_records'
    __table_args__ = (
        db.Index("dater", ri_date),
        {"schema": "augur_data"}
    )


class RepoLabor(db.Model):
    repo_labor_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_repo_labor_repo_1'))
    repo_clone_date = db.Column(db.TIMESTAMP())
    rl_analysis_date = db.Column(db.TIMESTAMP())
    programming_language = db.Column(db.String())
    file_path = db.Column(db.String())
    file_name = db.Column(db.String())
    total_lines = db.Column(db.Integer)
    code_lines = db.Column(db.Integer)
    comment_lines = db.Column(db.Integer)
    blank_lines = db.Column(db.Integer)
    code_complexity = db.Column(db.Integer)
    repo_url = db.Column(db.String(
    ), comment="This is a convenience column to simplify analysis against external datasets")
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_labor'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": "repo_labor is a derivative of tables used to store scc code and complexity counting statistics that are inputs to labor analysis, which are components of CHAOSS value metric calculations. "}
    )


class RepoMeta(db.Model):
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_repo_meta_repo_1'), primary_key=True, nullable=False)
    rmeta_id = db.Column(db.BigInteger,  primary_key=True, nullable=False)
    rmeta_name = db.Column(db.String())
    rmeta_value = db.Column(db.String(), server_default=text('0'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_meta'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": "Project Languages"}
    )


class RepoSbomScans(db.Model):
    rsb_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.Integer, db.ForeignKey('augur_data.repo.repo_id',
                        name='repo_linker_sbom', ondelete="CASCADE", onupdate="CASCADE"))
    sbom_scan = db.Column(db.JSON())

    __tablename__ = 'repo_sbom_scans'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class RepoStats(db.Model):
    repo_id = db.Column(db.BigInteger, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_repo_stats_repo_1'), primary_key=True, nullable=False)
    rstat_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    rstat_name = db.Column(db.String())
    rstat_value = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_stats'
    __table_args__ = (
        {"schema": "augur_data",
         "comment": "Project Watchers"}
    )


class RepoTestCoverage(db.Model):
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id',
                        name='fk_repo_test_coverage_repo_1'), primary_key=True, nullable=False)
    repo_clone_date = db.Column(db.TIMESTAMP())
    rtc_analysis_date = db.Column(db.TIMESTAMP())
    programming_language = db.Column(db.String())
    file_path = db.Column(db.String())
    file_name = db.Column(db.String())
    testing_tool = db.Column(db.String())
    file_statement_count = db.Column(db.BigInteger)
    file_subroutine_count = db.Column(db.BigInteger)
    file_statements_tested = db.Column(db.BigInteger)
    file_subroutines_tested = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_test_coverage'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class RepoTopic(db.Model):
    repo_topic_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.Integer, db.ForeignKey(
        'augur_data.repo.repo_id', name='fk_repo_topic_repo_1'))
    topic_id = db.Column(db.Integer)
    topic_prob = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'repo_topic'
    __table_args__ = (
        {"schema": "augur_data"}
    )

# TODO: Add foreign key to repo table


class ReposFetchLog(db.Model):
    repos_fetch_log_id = db.Column(db.BigInteger, primary_key=True)
    repos_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(), nullable=False)
    date = db.Column(db.TIMESTAMP(), nullable=False,
                     server_default=func.current_timestamp())

    __tablename__ = 'repos_fetch_log'
    __table_args__ = (
        # TODO: There appear to be two identical indexes
        db.Index("repos_id,status", repos_id, status),
        {"schema": "augur_data"}
    )


class Settings(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    setting = db.Column(db.String(), nullable=False)
    value = db.Column(db.String(), nullable=False)
    last_modified = db.Column(
        db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

    __tablename__ = 'settings'
    __table_args__ = (
        {"schema": "augur_data"}
    )


class TopicWords(db.Model):
    topic_words_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    topic_id = db.Column(db.BigInteger)
    word = db.Column(db.String())
    word_prob = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'topic_words'
    __table_args__ = (
        {"schema": "augur_data"}
    )

# TODO: Add foreign key to repo_group table


class UnknownCache(db.Model):
    unknown_cache_id = db.Column(db.BigInteger, primary_key=True)
    type = db.Column(db.String(), nullable=False)
    repo_group_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(), nullable=False)
    domain = db.Column(db.String(), server_default='NULL')
    added = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'unknown_cache'
    __table_args__ = (
        db.Index("type,projects_id", type, repo_group_id),
        {"schema": "augur_data"}
    )


class UnresolvedCommitEmails(db.Model):
    email_unresolved_id = db.Column(
        db.BigInteger, primary_key=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    name = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'unresolved_commit_emails'
    __table_args__ = (
        UniqueConstraint('email', name='unresolved_commit_emails_email_key'),
        {"schema": "augur_data"}
    )


class UtilityLog(db.Model):
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    level = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False)
    attempted = db.Column(db.TIMESTAMP(), nullable=False,
                          server_default=func.current_timestamp())

    __tablename__ = 'utility_log'
    __table_args__ = (
        {"schema": "augur_data"}
    )

# TODO: Add foreign key to repo table


class WorkingCommits(db.Model):
    working_commits_id = db.Column(db.BigInteger, primary_key=True)
    repos_id = db.Column(db.Integer, nullable=False)
    working_commit = db.Column(db.String(), server_default='NULL')

    __tablename__ = 'working_commits'
    __table_args__ = (
        {"schema": "augur_data"}
    )


# Start of Augur Operations tablespoon
class All(db.Model):
    all_id = db.Column(db.BigInteger, primary_key=True)
    Name = db.Column(db.String())
    Bytes = db.Column(db.String())
    Lines = db.Column(db.String())
    Code = db.Column(db.String())
    Comment = db.Column(db.String())
    Blank = db.Column(db.String())
    Complexity = db.Column(db.String())
    Count = db.Column(db.String())
    WeightedComplexity = db.Column(db.String())
    Files = db.Column(db.String())

    __tablename__ = 'all'
    __table_args__ = ({"schema": "augur_operations"})


class AugurSettings(db.Model):
    id = db.Column(db.BigInteger)
    setting = db.Column(db.String())
    value = db.Column(db.String())
    last_modified = db.Column(
        db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'augur_settings'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('setting', name='setting-unique'),
        {"schema": "augur_operations"}
    )


# class ReposFetchLog(db.Model):
#     repos_fetch_log_id = db.Column(db.BigInteger)
#     repos_id = db.Column(db.Integer, nullable=False)
#     status = db.Column(db.String(), nullable=False)
#     date = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

#     __tablename__ = 'repos_fetch_log'
#     __table_args__ = (
#         PrimaryKeyConstraint('repos_fetch_log_id'),
#         db.Index("repos_id,statusops", repos_id, status),
#         {"schema":"augur_operations"}
#     )

# TODO: Add foreign key to Repo table
class WorkerHistory(db.Model):
    history_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    worker = db.Column(db.String(), nullable=False)
    job_model = db.Column(db.String(), nullable=False)
    oauth_id = db.Column(db.Integer)
    timestamp = db.Column(db.TIMESTAMP(), nullable=False)
    status = db.Column(db.String(), nullable=False)
    total_results = db.Column(db.Integer)

    __tablename__ = 'worker_history'
    __table_args__ = (
        PrimaryKeyConstraint('history_id', name='history_pkey'),
        {"schema": "augur_operations"}
    )


class WorkerJob(db.Model):
    job_model = db.Column(db.String())
    state = db.Column(db.Integer, nullable=False, server_default=text('0'))
    zombie_head = db.Column(db.Integer)
    since_id_str = db.Column(db.String(), nullable=False, server_default='0')
    description = db.Column(db.String(), server_default='None')
    last_count = db.Column(db.Integer)
    last_run = db.Column(db.TIMESTAMP())
    analysis_state = db.Column(db.Integer, server_default=text('0'))
    oauth_id = db.Column(db.Integer, nullable=False)

    __tablename__ = 'worker_job'
    __table_args__ = (
        PrimaryKeyConstraint('job_model', name='job_pkey'),
        {"schema": "augur_operations"}
    )


class WorkerOauth(db.Model):
    oauth_id = db.Column(db.BigInteger)
    name = db.Column(db.String(), nullable=False)
    consumer_key = db.Column(db.String(), nullable=False)
    consumer_secret = db.Column(db.String(), nullable=False)
    access_token = db.Column(db.String(), nullable=False)
    access_token_secret = db.Column(db.String(), nullable=False)
    repo_directory = db.Column(db.String())
    platform = db.Column(db.String(), server_default='github')

    __tablename__ = 'worker_oauth'
    __table_args__ = (
        PrimaryKeyConstraint('oauth_id'),
        {"schema": "augur_operations"}
    )


class WorkerSettingsFacade(db.Model):
    id = db.Column(db.Integer)
    setting = db.Column(db.String(), nullable=False)
    value = db.Column(db.String(), nullable=False)
    last_modified = db.Column(
        db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

    __tablename__ = 'worker_settings_facade'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='settings_pkey'),
        {"schema": "augur_operations"}
    )


# class WorkingCommits(db.Model):
#     working_commits_id = db.Column(db.BigInteger)
#     repos_id = db.Column(db.Integer, nullable=False)
#     working_commit = db.Column(db.String())

#     __tablename__ = 'working_commits'
#     __table_args__ = (
#         PrimaryKeyConstraint('working_commits_id'),
#         {"schema":"augur_operations"}
#     )


class AnnotationTypes(db.Model):
    annotation_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    __tablename__ = 'annotation_types'
    __table_args__ = (
        UniqueConstraint('name', name='uc_annotation_type_name'),
        {"schema": "spdx"}
    )


class Annotations(db.Model):
    annotation_id = db.Column(db.Integer, primary_key=True, nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.documents.document_id', name='annotations_document_id_fkey'), nullable=False)
    annotation_type_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.annotation_types.annotation_type_id', name='annotations_annotation_type_id_fkey'), nullable=False)
    identifier_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.identifiers.identifier_id', name='annotations_identifier_id_fkey'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.creators.creator_id', name='annotations_creator_id_fkey'), nullable=False)
    created_ts = db.Column(db.TIMESTAMP(timezone=True))
    comment = db.Column(db.Text(), nullable=False)

    __tablename__ = 'annotations'
    __table_args__ = (
        {"schema": "spdx"}
    )


class AugurRepoMap(db.Model):
    map_id = db.Column(db.Integer, primary_key=True, nullable=False)
    dosocs_pkg_id = db.Column(db.Integer)
    dosocs_pkg_name = db.Column(db.Text())
    repo_id = db.Column(db.Integer)
    repo_path = db.Column(db.Text())

    __tablename__ = 'augur_repo_map'
    __table_args__ = ({"schema": "spdx"})


class CreatorTypes(db.Model):
    creator_type_id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(), nullable=False)

    __tablename__ = 'creator_types'
    __table_args__ = ({"schema": "spdx"})


class Creators(db.Model):
    creator_id = db.Column(db.Integer, primary_key=True, nullable=False)
    creator_type_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.creator_types.creator_type_id', name='creators_creator_type_id_fkey'), nullable=False)
    name = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)

    __tablename__ = 'creators'
    __table_args__ = ({"schema": "spdx"})


class DocumentNamespaces(db.Model):
    document_namespace_id = db.Column(
        db.Integer, primary_key=True, nullable=False)
    uri = db.Column(db.String(), nullable=False)

    __tablename__ = 'document_namespaces'
    __table_args__ = (
        UniqueConstraint('uri', name='uc_document_namespace_uri'),
        {"schema": "spdx"}
    )


class Documents(db.Model):
    document_id = db.Column(db.Integer, primary_key=True, nullable=False)
    document_namespace_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.document_namespaces.document_namespace_id', name='documents_document_namespace_id_fkey'), nullable=False)
    data_license_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.licenses.license_id', name='documents_data_license_id_fkey'), nullable=False)
    spdx_version = db.Column(db.String(), nullable=False)
    name = db.Column(db.String(), nullable=False)
    license_list_version = db.Column(db.String(), nullable=False)
    created_ts = db.Column(db.TIMESTAMP(timezone=True), nullable=False)
    creator_comment = db.Column(db.Text(), nullable=False)
    document_comment = db.Column(db.Text(), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.packages.package_id', name='documents_package_id_fkey'), nullable=False)

    __tablename__ = 'documents'
    __table_args__ = (
        UniqueConstraint('document_namespace_id',
                         name='uc_document_document_namespace_id'),
        {"schema": "spdx"}
    )


class DocumentsCreators(db.Model):
    document_creator_id = db.Column(
        db.Integer, primary_key=True, nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.documents.document_id', name='documents_creators_document_id_fkey'), nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.creators.creator_id', name='documents_creators_creator_id_fkey'), nullable=False)

    __tablename__ = 'documents_creators'
    __table_args__ = ({"schema": "spdx"})


class ExternalRefs(db.Model):
    external_ref_id = db.Column(db.Integer, primary_key=True, nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.documents.document_id', name='external_refs_document_id_fkey'), nullable=False)
    document_namespace_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.document_namespaces.document_namespace_id', name='external_refs_document_namespace_id_fkey'), nullable=False)
    id_string = db.Column(db.String(), nullable=False)
    sha256 = db.Column(db.String(), nullable=False)

    __tablename__ = 'external_refs'
    __table_args__ = (
        UniqueConstraint('document_id', 'id_string',
                         name='uc_external_ref_document_id_string'),
        {"schema": "spdx"}
    )


class FileContributors(db.Model):
    file_contributor_id = db.Column(
        db.Integer, primary_key=True, nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.files.file_id', name='file_contributors_file_id_fkey'), nullable=False)
    contributor = db.Column(db.Text(), nullable=False)

    __tablename__ = 'file_contributors'
    __table_args__ = ({"schema": "spdx"})


class FileTypes(db.Model):
    file_type_id = db.Column(db.Integer)
    name = db.Column(db.String(), nullable=False)

    __tablename__ = 'file_types'
    __table_args__ = (
        PrimaryKeyConstraint('name', name='uc_file_type_name'),
        {"schema": "spdx"}
    )


class Files(db.Model):
    file_id = db.Column(db.Integer, primary_key=True, nullable=False)
    file_type_id = db.Column(db.Integer)
    sha256 = db.Column(db.String(), nullable=False)
    copyright_text = db.Column(db.Text())
    package_id = db.Column(db.Integer)
    comment = db.Column(db.Text(), nullable=False)
    notice = db.Column(db.Text(), nullable=False)

    __tablename__ = 'files'
    __table_args__ = (
        UniqueConstraint('sha256', name='uc_file_sha256'),
        {"schema": "spdx"}
    )


class FilesLicenses(db.Model):
    file_license_id = db.Column(db.Integer, primary_key=True, nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.files.file_id', name='files_licenses_file_id_fkey'), nullable=False)
    license_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.licenses.license_id', name='files_licenses_license_id_fkey'), nullable=False)
    extracted_text = db.Column(db.Text(), nullable=False)

    __tablename__ = 'files_licenses'
    __table_args__ = (
        UniqueConstraint('file_id', 'license_id', name='uc_file_license'),
        {"schema": "spdx"}
    )


class FilesScans(db.Model):
    file_scan_id = db.Column(db.Integer, primary_key=True, nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.files.file_id', name='files_scans_file_id_fkey'), nullable=False)
    scanner_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.scanners.scanner_id', name='files_scans_scanner_id_fkey'), nullable=False)

    __tablename__ = 'files_scans'
    __table_args__ = (
        UniqueConstraint('file_id', 'scanner_id', name='uc_file_scanner_id'),
        {"schema": "spdx"}
    )

# TODO: Add check to table


class Identifiers(db.Model):
    identifier_id = db.Column(db.Integer, primary_key=True, nullable=False)
    document_namespace_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.document_namespaces.document_namespace_id', name='identifiers_document_namespace_id_fkey'), nullable=False)
    id_string = db.Column(db.String(), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.documents.document_id', name='identifiers_document_id_fkey'))
    package_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.packages.package_id', name='identifiers_package_id_fkey'))
    package_file_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.packages_files.package_file_id', name='identifiers_package_file_id_fkey'))

    __tablename__ = 'identifiers'
    __table_args__ = (
        UniqueConstraint('document_namespace_id', 'id_string',
                         name='uc_identifier_document_namespace_id'),
        UniqueConstraint('document_namespace_id', 'document_id',
                         name='uc_identifier_namespace_document_id'),
        UniqueConstraint('document_namespace_id', 'package_id',
                         name='uc_identifier_namespace_package_id'),
        UniqueConstraint('document_namespace_id', 'package_file_id',
                         name='uc_identifier_namespace_package_file_id'),
        {"schema": "spdx"}
    )


class Licenses(db.Model):
    license_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    short_name = db.Column(db.String(), nullable=False)
    cross_reference = db.Column(db.Text(), nullable=False)
    comment = db.Column(db.Text(), nullable=False)
    is_spdx_official = db.Column(db.Boolean(), nullable=False)

    __tablename__ = 'licenses'
    __table_args__ = (
        UniqueConstraint('short_name', name='uc_license_short_name'),
        {"schema": "spdx"}
    )

# TODO: Need to a check


class Packages(db.Model):
    package_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    version = db.Column(db.String(), nullable=False)
    file_name = db.Column(db.Text(), nullable=False)
    supplier_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.creators.creator_id', name='packages_supplier_id_fkey'))
    originator_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.creators.creator_id', name='packages_originator_id_fkey'))
    download_location = db.Column(db.Text())
    verification_code = db.Column(db.String(), nullable=False)
    ver_code_excluded_file_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.packages_files.package_file_id', name='fk_package_packages_files'))
    sha256 = db.Column(db.String())
    home_page = db.Column(db.Text())
    source_info = db.Column(db.Text(), nullable=False)
    concluded_license_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.licenses.license_id', name='packages_concluded_license_id_fkey'))
    declared_license_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.licenses.license_id', name='packages_declared_license_id_fkey'))
    license_comment = db.Column(db.Text(), nullable=False)
    copyright_text = db.Column(db.Text())
    summary = db.Column(db.Text(), nullable=False)
    description = db.Column(db.Text(), nullable=False)
    comment = db.Column(db.Text(), nullable=False)
    dosocs2_dir_code = db.Column(db.String())

    __tablename__ = 'packages'
    __table_args__ = (
        UniqueConstraint('sha256', name='uc_package_sha256'),
        UniqueConstraint('verification_code', 'dosocs2_dir_code',
                         name='uc_dir_code_ver_code'),
        {"schema": "spdx"}
    )


class PackagesFiles(db.Model):
    package_file_id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.packages.package_id', name='fk_package_files_packages'), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.files.file_id', name='packages_files_file_id_fkey'), nullable=False)
    concluded_license_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.licenses.license_id', name='packages_files_concluded_license_id_fkey'))
    license_comment = db.Column(db.Text(), nullable=False)
    file_name = db.Column(db.Text(), nullable=False)

    __tablename__ = 'packages_files'
    __table_args__ = (
        UniqueConstraint('package_id', 'file_name',
                         name='uc_package_id_file_name'),
        {"schema": "spdx"}
    )


class PackagesScans(db.Model):
    package_scan_id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.packages.package_id', name='packages_scans_package_id_fkey'), nullable=False)
    scanner_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.scanners.scanner_id', name='packages_scans_scanner_id_fkey'), nullable=False)

    __tablename__ = 'packages_scans'
    __table_args__ = (
        UniqueConstraint('package_id', 'scanner_id',
                         name='uc_package_scanner_id'),
        {"schema": "spdx"}
    )


class Projects(db.Model):
    package_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text(), nullable=False)
    homepage = db.Column(db.Text(), nullable=False)
    uri = db.Column(db.Text(), nullable=False)

    __tablename__ = 'projects'
    __table_args__ = (
        {"schema": "spdx"}
    )


class RelationshipTypes(db.Model):
    relationship_type_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    __tablename__ = 'relationship_types'
    __table_args__ = (
        UniqueConstraint('name', name='uc_relationship_type_name'),
        {"schema": "spdx"}
    )


class Relationships(db.Model):
    relationship_id = db.Column(db.Integer, primary_key=True)
    left_identifier_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.identifiers.identifier_id', name='relationships_left_identifier_id_fkey'), nullable=False)
    right_identifier_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.identifiers.identifier_id', name='relationships_right_identifier_id_fkey'), nullable=False)
    relationship_type_id = db.Column(db.Integer, db.ForeignKey(
        'spdx.relationship_types.relationship_type_id', name='relationships_relationship_type_id_fkey'), nullable=False)
    relationship_comment = db.Column(db.Text(), nullable=False)

    __tablename__ = 'relationships'
    __table_args__ = (
        UniqueConstraint('left_identifier_id', 'right_identifier_id',
                         'relationship_type_id', name='uc_left_right_relationship_type'),
        {"schema": "spdx"}
    )


class SbomScans(db.Model):
    sbom_scan_id = db.Column(db.Integer, primary_key=True)
    repo_id = db.Column(db.Integer)
    sbom_scan = db.Column(db.JSON())

    __tablename__ = 'sbom_scans'
    __table_args__ = (
        {"schema": "spdx"}
    )


class Scanners(db.Model):
    scanner_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)

    __tablename__ = 'scanners'
    __table_args__ = (
        UniqueConstraint('name', name='uc_scanner_name'),
        {"schema": "spdx"}
    )


if __name__ == '__main__':
    app.run(debug=True)

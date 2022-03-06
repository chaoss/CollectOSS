from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Import the flask app
# app = Flask(__name__)

# define the database connection string for Flask app
# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'

# TODO: Create db from Flask app
db = SQLAlchemy(app)
# TODO: need to add default of current timestamp for data_collection_date
# TODO: how to define schemas
# TODO: how to add indexes
# TODO: Sqlalchemey defines timestamp with length of 6


# TODO: Sqlalchemey defines timestamp with length of 6

# TODO: removed asc and dsc from hash indexes because they are not supported (it automatically set them to ASC NULLS LAST which is the same as all the ones in the database)
# TODO: Foreign keys should also be not null to make it more clear a row can't be added without it


# TODO: Added primary key
class AnalysisLog(db.Model):
    __tablename__ = 'analysis_log'
    __table_args__ = {"schema": "augur_data"}
    repos_id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.String(), primary_key=True, nullable=False)
    date_attempted = db.Column(db.TIMESTAMP(), nullable=False, default=datetime.now())


Index("repos_id", AnalysisLog.repos_id.asc().nullslast())


class ChaossMetricStatus(db.Model):
    __tablename__ = 'chaoss_metric_status'
    __table_args__ = {"schema": "augur_data"}
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())
    cm_working_group_focus_area = db.Column(db.String())


class CommitCommentRef(db.Model):
    __tablename__ = 'commit_comment_ref'
    __table_args__ = {"schema": "augur_data"}
    cmt_comment_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cmt_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.commits.cmt_id', name='fk_commit_comment_ref_commits_1',
                                                    onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    repo_id = db.Column(db.BigInteger)
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_commit_comment_ref_message_1',
                                                    onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    user_id = db.Column(db.BigInteger, nullable=False)
    body = db.Column(db.Text())
    line = db.Column(db.BigInteger)
    position = db.Column(db.BigInteger)
    commit_comment_src_node_id = db.Column(db.String())
    cmt_comment_src_id = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.TIMESTAMP(), nullable=False, default=datetime.now())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("comment_id", CommitCommentRef.cmt_comment_src_id.asc().nullslast(),
      CommitCommentRef.cmt_comment_id.asc().nullslast(), CommitCommentRef.msg_id.asc().nullslast())


class CommitParents(db.Model):
    __tablename__ = 'commit_parents'
    __table_args__ = {"schema": "augur_data"}
    cmt_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.commits.cmt_id', name='fk_commit_parents_commits_1'),
                       primary_key=True)
    parent_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.commits.cmt_id', name='fk_commit_parents_commits_2'),
                          primary_key=True)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("commit_parents_ibfk_1", CommitParents.cmt_id.asc().nullslast())
Index("commit_parents_ibfk_2", CommitParents.parent_id.asc().nullslast())


# TODO: Current db version has some varchar defined with length but I changed that with flask
# TODO: Add foriegn key: cmt_author_platform_username = db.Column(db.String(), db.ForeignKey('augur_data.contributors.cntrb_login', name='fk_commits_contributors_3', ondelete="CASCADE", onupdate="CASCADE"))
class Commits(db.Model):
    __tablename__ = 'commits'
    __table_args__ = {"schema": "augur_data"}
    cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_commits_repo_2', ondelete="RESTRICT",
                                      onupdate="CASCADE"), nullable=False)
    cmt_commit_hash = db.Column(db.String(), nullable=False)
    cmt_author_name = db.Column(db.String(), nullable=False)
    cmt_author_raw_email = db.Column(db.String(), nullable=False)
    cmt_author_email = db.Column(db.String(), nullable=False)
    cmt_author_date = db.Column(db.String(), nullable=False)
    cmt_author_affiliation = db.Column(db.String())
    cmt_committer_name = db.Column(db.String(), nullable=False)
    cmt_committer_raw_email = db.Column(db.String(), nullable=False)
    cmt_committer_email = db.Column(db.String(), nullable=False)
    cmt_committer_date = db.Column(db.String(), nullable=False)
    cmt_committer_affiliation = db.Column(db.String())
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("author_affiliation", Commits.cmt_author_affiliation, postgresql_using='hash')

Index("author_cntrb_id", Commits.cmt_ght_author_id.asc().nullslast())
Index("author_email,author_affiliation,author_date", Commits.cmt_author_email.asc().nullslast(),
      Commits.cmt_author_affiliation.asc().nullslast(), Commits.cmt_author_date.asc().nullslast())
Index("author_raw_email", Commits.cmt_author_raw_email.asc().nullslast())
Index("cmt-author-date-idx2", Commits.cmt_author_date.asc().nullslast())

Index("cmt_author_contrib_worker", Commits.cmt_author_name, Commits.cmt_author_email, Commits.cmt_author_date,
      postgresql_using='brin')
Index("cmt_commiter_contrib_worker", Commits.cmt_committer_name, Commits.cmt_committer_email,
      Commits.cmt_committer_date, postgresql_using='brin')

Index("commited", Commits.cmt_id.asc().nullslast())
Index("commits_idx_cmt_email_cmt_date_cmt_name", Commits.cmt_author_email.asc().nullslast(),
      Commits.cmt_author_date.asc().nullslast(), Commits.cmt_author_name.asc().nullslast())
Index("commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam", Commits.repo_id.asc().nullslast(),
      Commits.cmt_author_email.asc().nullslast(), Commits.cmt_author_date.asc().nullslast(),
      Commits.cmt_author_name.asc().nullslast())
Index("commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam2", Commits.repo_id.asc().nullslast(),
      Commits.cmt_committer_email.asc().nullslast(), Commits.cmt_committer_date.asc().nullslast(),
      Commits.cmt_committer_name.asc().nullslast())

Index("committer_affiliation", Commits.cmt_committer_affiliation, postgresql_using='hash')

Index("committer_email,committer_affiliation,committer_date", Commits.cmt_committer_email.asc().nullslast(),
      Commits.cmt_committer_affiliation.asc().nullslast(), Commits.cmt_committer_date.asc().nullslast())
Index("committer_raw_email", Commits.cmt_committer_raw_email.asc().nullslast())
Index("repo_id,commit", Commits.repo_id.asc().nullslast(), Commits.cmt_commit_hash.asc().nullslast())


# Current db has varchar with length but I changed that
class ContributorAffiliations(db.Model):
    __tablename__ = 'contributor_affiliations'
    __table_args__ = {"schema": "augur_data"}
    ca_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    ca_domain = db.Column(db.String(), nullable=False)
    ca_start_date = db.Column(db.Date)
    ca_last_used = db.Column(db.TIMESTAMP(), nullable=False)
    ca_affiliation = db.Column(db.String())
    ca_active = db.Column(db.SmallInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class ContributorRepo(db.Model):
    __tablename__ = 'contributor_repo'
    __table_args__ = {"schema": "augur_data"}
    cntrb_repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cntrb_id = db.Column(db.BigInteger,
                         db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_contributor_repo_contributors_1',
                                       ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    repo_git = db.Column(db.String(), nullable=False)
    repo_name = db.Column(db.String(), nullable=False)
    gh_repo_id = db.Column(db.BigInteger, nullable=False)
    cntrb_category = db.Column(db.String())
    event_id = db.Column(db.BigInteger)
    created_at = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class Contributors(db.Model):
    __tablename__ = 'contributors'
    __table_args__ = {"schema": "augur_data"}
    cntrb_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cntrb_login = db.Column(db.String())
    cntrb_email = db.Column(db.String())
    cntrb_full_name = db.Column(db.String())
    cntrb_company = db.Column(db.String())
    cntrb_created_at = db.Column(db.TIMESTAMP())
    cntrb_type = db.Column(db.String())
    cntrb_fake = db.Column(db.SmallInteger)
    cntrb_deleted = db.Column(db.SmallInteger)
    cntrb_long = db.Column(db.Numeric(precision=11, scale=8))
    cntrb_lat = db.Column(db.Numeric(precision=10, scale=8))
    cntrb_country_code = db.Column(db.CHAR(length=3))
    cntrb_state = db.Column(db.String())
    cntrb_city = db.Column(db.String())
    cntrb_location = db.Column(db.String())
    cntrb_canonical = db.Column(db.String())
    cntrb_last_used = db.Column(db.TIMESTAMP(timezone=True))
    gh_user_id = db.Column(db.BigInteger)
    gh_login = db.Column(db.String())
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("cnt-fullname", Contributors.cntrb_full_name, postgresql_using='hash')
Index("cntrb-theemail", Contributors.cntrb_email, postgresql_using='hash')

Index("cntrb_canonica-idx11", Contributors.cntrb_canonical.asc().nullslast())
Index("cntrb_login_platform_index", Contributors.cntrb_login.asc().nullslast())

Index("contributor_delete_finder", Contributors.cntrb_id, Contributors.cntrb_email, postgresql_using='brin')
Index("contributor_worker_email_finder", Contributors.cntrb_email, postgresql_using='brin')
Index("contributor_worker_finder", Contributors.cntrb_login, Contributors.cntrb_email, Contributors.cntrb_id,
      postgresql_using='brin')

# TODO: This index is the saem as the first one but one has a different stuff
Index("contributor_worker_fullname_finder", Contributors.cntrb_full_name, postgresql_using='brin')

Index("contributors_idx_cntrb_email3", Contributors.cntrb_email.asc().nullslast())

# TODO: These last onese appear to be the same
Index("login", Contributors.cntrb_login.asc().nullslast())
Index("login-contributor-idx", Contributors.cntrb_login.asc().nullslast())


class ContributorsAliases(db.Model):
    __tablename__ = 'contributors_aliases'
    __table_args__ = {"schema": "augur_data"}
    cntrb_alias_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                                                      name='fk_contributors_aliases_contributors_1', ondelete="CASCADE",
                                                      onupdate="CASCADE"), nullable=False)
    canonical_email = db.Column(db.String(), nullable=False)
    alias_email = db.Column(db.String(), nullable=False)
    cntrb_active = db.Column(db.SmallInteger, nullable=False)
    cntrb_last_modified = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


# TODO: msg_id should be not null since foreign key
class DiscourseInsights(db.Model):
    __tablename__ = 'discourse_insights'
    __table_args__ = {"schema": "augur_data"}
    msg_discourse_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    msg_id = db.Column(db.BigInteger,
                       db.ForeignKey('augur_data.message.msg_id', name='fk_discourse_insights_message_1'))
    discourse_act = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


# TODO Temporaily defined priimary key on first attribute so it would generate
class DmRepoAnnual(db.Model):
    __tablename__ = 'dm_repo_annual'
    __table_args__ = {"schema": "augur_data"}
    repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String())
    year = db.Column(db.SmallInteger, nullable=False)
    added = db.Column(db.BigInteger, nullable=False)
    removed = db.Column(db.BigInteger, nullable=False)
    whitespace = db.Column(db.BigInteger, nullable=False)
    files = db.Column(db.BigInteger, nullable=False)
    patches = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("repo_id,affiliation_copy_1", DmRepoAnnual.repo_id.asc().nullslast(), DmRepoAnnual.affiliation.asc().nullslast())
Index("repo_id,email_copy_1", DmRepoAnnual.repo_id.asc().nullslast(), DmRepoAnnual.email.asc().nullslast())


class DmRepoGroupAnnual(db.Model):
    __tablename__ = 'dm_repo_group_annual'
    __table_args__ = {"schema": "augur_data"}
    repo_group_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String())
    year = db.Column(db.SmallInteger, nullable=False)
    added = db.Column(db.BigInteger, nullable=False)
    removed = db.Column(db.BigInteger, nullable=False)
    whitespace = db.Column(db.BigInteger, nullable=False)
    files = db.Column(db.BigInteger, nullable=False)
    patches = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("projects_id,affiliation_copy_1", DmRepoGroupAnnual.repo_group_id.asc().nullslast(),
      DmRepoGroupAnnual.affiliation.asc().nullslast())
Index("projects_id,email_copy_1", DmRepoGroupAnnual.repo_group_id.asc().nullslast(),
      DmRepoGroupAnnual.email.asc().nullslast())


class DmRepoGroupMonthly(db.Model):
    __tablename__ = 'dm_repo_group_monthly'
    __table_args__ = {"schema": "augur_data"}
    repo_group_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String())
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("projects_id,affiliation_copy_2", DmRepoGroupMonthly.repo_group_id.asc().nullslast(),
      DmRepoGroupMonthly.affiliation.asc().nullslast())
Index("projects_id,email_copy_2", DmRepoGroupMonthly.repo_group_id.asc().nullslast(),
      DmRepoGroupMonthly.email.asc().nullslast())
Index("projects_id,year,affiliation_copy_1", DmRepoGroupMonthly.repo_group_id.asc().nullslast(),
      DmRepoGroupMonthly.year.asc().nullslast(), DmRepoGroupMonthly.affiliation.asc().nullslast())
Index("projects_id,year,email_copy_1", DmRepoGroupMonthly.repo_group_id.asc().nullslast(),
      DmRepoGroupMonthly.year.asc().nullslast(), DmRepoGroupMonthly.email.asc().nullslast())


class DmRepoGroupWeekly(db.Model):
    __tablename__ = 'dm_repo_group_weekly'
    __table_args__ = {"schema": "augur_data"}
    repo_group_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String())
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("projects_id,affiliation", DmRepoGroupWeekly.repo_group_id.asc().nullslast(),
      DmRepoGroupWeekly.affiliation.asc().nullslast())
Index("projects_id,email", DmRepoGroupWeekly.repo_group_id.asc().nullslast(), DmRepoGroupWeekly.email.asc().nullslast())
Index("projects_id,year,affiliation", DmRepoGroupWeekly.repo_group_id.asc().nullslast(),
      DmRepoGroupWeekly.year.asc().nullslast(), DmRepoGroupWeekly.affiliation.asc().nullslast())
Index("projects_id,year,email", DmRepoGroupWeekly.repo_group_id.asc().nullslast(),
      DmRepoGroupWeekly.year.asc().nullslast(), DmRepoGroupWeekly.email.asc().nullslast())


class DmRepoMonthly(db.Model):
    __tablename__ = 'dm_repo_monthly'
    __table_args__ = {"schema": "augur_data"}
    repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String())
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("repo_id,affiliation_copy_2", DmRepoMonthly.repo_id.asc().nullslast(),
      DmRepoMonthly.affiliation.asc().nullslast())
Index("repo_id,email_copy_2", DmRepoMonthly.repo_id.asc().nullslast(), DmRepoMonthly.email.asc().nullslast())
Index("repo_id,year,affiliation_copy_1", DmRepoMonthly.repo_id.asc().nullslast(), DmRepoMonthly.year.asc().nullslast(),
      DmRepoMonthly.affiliation.asc().nullslast())
Index("repo_id,year,email_copy_1", DmRepoMonthly.repo_id.asc().nullslast(), DmRepoMonthly.year.asc().nullslast(),
      DmRepoMonthly.email.asc().nullslast())


class DmRepoWeekly(db.Model):
    __tablename__ = 'dm_repo_weekly'
    __table_args__ = {"schema": "augur_data"}
    repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    affiliation = db.Column(db.String())
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("repo_id,affiliation", DmRepoWeekly.repo_id.asc().nullslast(), DmRepoWeekly.affiliation.asc().nullslast())
Index("repo_id,email", DmRepoWeekly.repo_id.asc().nullslast(), DmRepoWeekly.email.asc().nullslast())
Index("repo_id,year,affiliation", DmRepoWeekly.repo_id.asc().nullslast(), DmRepoWeekly.year.asc().nullslast(),
      DmRepoWeekly.affiliation.asc().nullslast())
Index("repo_id,year,email", DmRepoWeekly.repo_id.asc().nullslast(), DmRepoWeekly.year.asc().nullslast(),
      DmRepoWeekly.email.asc().nullslast())


class Exclude(db.Model):
    __tablename__ = 'exclude'
    __table_args__ = {"schema": "augur_data"}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    projects_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String())
    domain = db.Column(db.String())


class IssueAssignees(db.Model):
    __tablename__ = 'issue_assignees'
    __table_args__ = {"schema": "augur_data"}
    issue_assignee_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.issues.issue_id', name='fk_issue_assignees_issues_1'))
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_issue_assignee_repo_id', ondelete="RESTRICT",
                                      onupdate="CASCADE"))
    cntrb_id = db.Column(db.BigInteger,
                         db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_issue_assignees_contributors_1'))
    issue_assignee_src_id = db.Column(db.BigInteger)
    issue_assignee_src_node = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("issue-cntrb-assign-idx-1", IssueAssignees.cntrb_id.asc().nullslast())


class IssueEvents(db.Model):
    __tablename__ = 'issue_events'
    __table_args__ = {"schema": "augur_data"}
    event_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.issues.issue_id', name='fk_issue_events_issues_1',
                                                      ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_issue_events_repo', ondelete="RESTRICT",
                                      onupdate="CASCADE"))
    cntrb_id = db.Column(db.BigInteger,
                         db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_issue_events_contributors_1',
                                       ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    action = db.Column(db.String(), nullable=False)
    action_commit_hash = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP(), nullable=False, default=datetime.now())
    node_id = db.Column(db.String())
    node_url = db.Column(db.String())
    issue_event_src_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())
    platform_id = db.Column(db.BigInteger,
                            db.ForeignKey('augur_data.platform.pltfrm_id', name='fk_issue_event_platform_ide',
                                          ondelete="RESTRICT", onupdate="CASCADE"))


Index("issue-cntrb-idx2", IssueEvents.issue_event_src_id.asc().nullslast())
Index("issue_events_ibfk_1", IssueEvents.issue_id.asc().nullslast())
Index("issue_events_ibfk_2", IssueEvents.cntrb_id.asc().nullslast())


class IssueLabels(db.Model):
    __tablename__ = 'issue_labels'
    __table_args__ = {"schema": "augur_data"}
    issue_label_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.issues.issue_id', name='fk_issue_labels_issues_1'),
                         nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_issue_labels_repo_id', ondelete="RESTRICT",
                                      onupdate="CASCADE"))
    label_text = db.Column(db.String())
    label_description = db.Column(db.String())
    label_color = db.Column(db.String())
    label_src_id = db.Column(db.BigInteger)
    label_src_node_id = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class IssueMessageRef(db.Model):
    __tablename__ = 'issue_message_ref'
    __table_args__ = {"schema": "augur_data"}
    issue_msg_ref_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger,
                         db.ForeignKey('augur_data.issues.issue_id', name='fk_issue_message_ref_issues_1',
                                       ondelete="RESTRICT", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_id_fk1', ondelete="RESTRICT",
                                      onupdate="CASCADE"))
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_issue_message_ref_message_1',
                                                    ondelete="RESTRICT", onupdate="CASCADE"))
    issue_msg_ref_src_node_id = db.Column(db.String())
    issue_msg_ref_src_comment_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


# should repo_id be allowed to be NULL?
class Issues(db.Model):
    __tablename__ = 'issues'
    __table_args__ = {"schema": "augur_data"}
    issue_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_issues_repo', ondelete="CASCADE",
                                      onupdate="CASCADE"))
    reporter_id = db.Column(db.BigInteger,
                            db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_issues_contributors_2'))
    pull_request = db.Column(db.BigInteger)
    pull_request_id = db.Column(db.BigInteger)
    created_at = db.Column(db.TIMESTAMP())
    issue_title = db.Column(db.String())
    issue_body = db.Column(db.String())
    cntrb_id = db.Column(db.BigInteger,
                         db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_issues_contributors_1'))
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("issue-cntrb-dix2", Issues.cntrb_id.asc().nullslast())
Index("issues_ibfk_1", Issues.repo_id.asc().nullslast())
Index("issues_ibfk_2", Issues.reporter_id.asc().nullslast())
Index("issues_ibfk_4", Issues.pull_request_id.asc().nullslast())


# TODO: Should latest_release_timestamp be a timestamp
class Libraries(db.Model):
    __tablename__ = 'libraries'
    __table_args__ = {"schema": "augur_data"}
    library_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_libraries_repo_1'))
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class LibraryDependecies(db.Model):
    __tablename__ = 'library_dependencies'
    __table_args__ = {"schema": "augur_data"}
    lib_dependency_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    library_id = db.Column(db.BigInteger,
                           db.ForeignKey('augur_data.libraries.library_id', name='fk_library_dependencies_libraries_1'))
    manifest_platform = db.Column(db.String())
    manifest_filepath = db.Column(db.String())
    manifest_kind = db.Column(db.String())
    repo_id_branch = db.Column(db.String(), nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("REPO_DEP", LibraryDependecies.library_id.asc().nullslast())


class LibraryVersion(db.Model):
    __tablename__ = 'library_version'
    __table_args__ = {"schema": "augur_data"}
    library_version_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    library_id = db.Column(db.BigInteger,
                           db.ForeignKey('augur_data.libraries.library_id', name='fk_library_version_libraries_1'))
    library_platform = db.Column(db.String())
    version_number = db.Column(db.String())
    version_release_date = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class LstmAnomalyModels(db.Model):
    __tablename__ = 'lstm_anomaly_models'
    __table_args__ = {"schema": "augur_data"}
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class LstmAnomalyResults(db.Model):
    __tablename__ = 'lstm_anomaly_results'
    __table_args__ = {"schema": "augur_data"}
    result_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_lstm_anomaly_results_repo_1'))
    repo_category = db.Column(db.String())
    model_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.lstm_anomaly_models.model_id',
                                                      name='fk_lstm_anomaly_results_lstm_anomaly_models_1'))
    metric = db.Column(db.String())
    contamination_factor = db.Column(db.Float())
    mean_absolute_error = db.Column(db.Float())
    remarks = db.Column(db.String())
    metric_field = db.Column(db.String())
    mean_absolute_actual_value = db.Column(db.Float())
    mean_absolute_prediction_value = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class Message(db.Model):
    __tablename__ = 'message'
    __table_args__ = {"schema": "augur_data"}
    msg_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    rgls_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo_groups_list_serve.rgls_id',
                                                     name='fk_message_repo_groups_list_serve_1', ondelete="CASCADE",
                                                     onupdate="CASCADE"))
    platform_msg_id = db.Column(db.BigInteger)
    platform_node_id = db.Column(db.String())
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_message_repoid', ondelete="CASCADE",
                                      onupdate="CASCADE"))
    cntrb_id = db.Column(db.BigInteger,
                         db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_message_contributors_1',
                                       ondelete="CASCADE", onupdate="CASCADE"))
    msg_text = db.Column(db.String())
    msg_timestamp = db.Column(db.TIMESTAMP())
    msg_sender_email = db.Column(db.String())
    msg_header = db.Column(db.String())
    pltfrm_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.platform.pltfrm_id', name='fk_message_platform_1',
                                                       ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("messagegrouper", Message.msg_id.asc().nullslast(),
      Message.rgls_id.asc().nullslast(), unique=True)
Index("msg-cntrb-id-idx", Message.cntrb_id.asc().nullslast())
Index("platformgrouper", Message.msg_id.asc().nullslast(),
      Message.pltfrm_id.asc().nullslast())


class MessageAnalysis(db.Model):
    __tablename__ = 'message_analysis'
    __table_args__ = {"schema": "augur_data"}
    msg_analysis_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_message_analysis_message_1'))
    worker_run_id = db.Column(db.BigInteger)
    sentiment_score = db.Column(db.Float())
    reconstruction_error = db.Column(db.Float())
    novelty_flag = db.Column(db.Boolean())
    feedback_flag = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class MessageAnalysisSummary(db.Model):
    __tablename__ = 'message_analysis_summary'
    __table_args__ = {"schema": "augur_data"}
    msg_summary_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_message_analysis_summary_repo_1'))
    worker_run_id = db.Column(db.BigInteger)
    positive_ratio = db.Column(db.Float())
    negative_ratio = db.Column(db.Float())
    novel_count = db.Column(db.BigInteger)
    period = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class MessageSentiment(db.Model):
    __tablename__ = 'message_sentiment'
    __table_args__ = {"schema": "augur_data"}
    msg_analysis_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_message_sentiment_message_1'))
    worker_run_id = db.Column(db.BigInteger)
    sentiment_score = db.Column(db.Float())
    reconstruction_error = db.Column(db.Float())
    novelty_flag = db.Column(db.Boolean())
    feedback_flag = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class MessageSentimentSummary(db.Model):
    __tablename__ = 'message_sentiment_summary'
    __table_args__ = {"schema": "augur_data"}
    msg_summary_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_message_sentiment_summary_repo_1'))
    worker_run_id = db.Column(db.BigInteger)
    positive_ratio = db.Column(db.Float())
    negative_ratio = db.Column(db.Float())
    novel_count = db.Column(db.BigInteger)
    period = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class Platform(db.Model):
    __tablename__ = 'platform'
    __table_args__ = {"schema": "augur_data"}
    pltfrm_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pltfrm_name = db.Column(db.String())
    pltfrm_version = db.Column(db.String())
    pltfrm_release_date = db.Column(db.Date)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("plat", Platform.pltfrm_id.asc().nullslast(), unique=True)


class PullRequestAnalysis(db.Model):
    __tablename__ = 'pull_request_analysis'
    __table_args__ = {"schema": "augur_data"}
    pull_request_analysis_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_analysis_pull_requests_1',
                                                             ondelete="CASCADE", onupdate="CASCADE"))
    merge_probability = db.Column(db.Numeric(precision=256, scale=250))
    mechanism = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("pr_anal_idx", PullRequestAnalysis.pull_request_id.asc().nullslast())
Index("probability_idx", PullRequestAnalysis.merge_probability.desc().nullslast())


class PullRequestAssignees(db.Model):
    __tablename__ = 'pull_request_assignees'
    __table_args__ = {"schema": "augur_data"}
    pr_assignee_map_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_assignees_pull_requests_1'))
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_assignees_repo_id',
                                      ondelete="RESTRICT", onupdate="CASCADE"))
    contrib_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                                                        name='fk_pull_request_assignees_contributors_1'))
    pr_assignee_src_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("pr_meta_cntrb-idx", PullRequestAssignees.contrib_id.asc().nullslast())


class PullRequestCommits(db.Model):
    __tablename__ = 'pull_request_commits'
    __table_args__ = {"schema": "augur_data"}
    pr_cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_commits_pull_requests_1',
                                                             ondelete="CASCADE", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_commits_repo_id',
                                                     ondelete="RESTRICT", onupdate="CASCADE"))
    pr_cmt_sha = db.Column(db.String())
    pr_cmt_node_id = db.Column(db.String())
    pr_cmt_message = db.Column(db.String())
    # TODO: varbit in database can't find sqlalchemy equivalent
    pr_cmt_comments_url = db.Column(db.LargeBinary())
    pr_cmt_author_cntrb_id = db.Column(db.BigInteger,
                                       db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pr_commit_cntrb_id',
                                                     ondelete="CASCADE", onupdate="CASCADE"))
    pr_cmt_timestamp = db.Column(db.TIMESTAMP())
    pr_cmt_author_email = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class PullRequestEvents(db.Model):
    __tablename__ = 'pull_request_events'
    __table_args__ = {"schema": "augur_data"}
    pr_event_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_events_pull_requests_1',
                                                             ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fkprevent_repo_id', ondelete="RESTRICT",
                                      onupdate="RESTRICT"))
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                                                      name='fk_pull_request_events_contributors_1'), nullable=False)
    action = db.Column(db.String(), nullable=False)
    action_commit_hash = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP(), nullable=False, default=datetime.now())
    issue_event_src_id = db.Column(db.BigInteger)
    node_id = db.Column(db.String())
    node_url = db.Column(db.String())
    platform_id = db.Column(db.BigInteger,
                            db.ForeignKey('augur_data.platform.pltfrm_id', name='fkpr_platform', ondelete="RESTRICT",
                                          onupdate="RESTRICT"))
    pr_platform_event_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("pr_events_ibfk_1", PullRequestEvents.pull_request_id.asc().nullslast())
Index("pr_events_ibfk_2", PullRequestEvents.cntrb_id.asc().nullslast())


class PullRequestFiles(db.Model):
    __tablename__ = 'pull_request_files'
    __table_args__ = {"schema": "augur_data"}
    pr_file_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_commits_pull_requests_1_copy_1',
                                                             ondelete="CASCADE", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_files_repo_id',
                                                     ondelete="RESTRICT", onupdate="CASCADE"))
    pr_file_additions = db.Column(db.BigInteger)
    pr_file_deletions = db.Column(db.BigInteger)
    pr_file_path = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class PullRequestLabels(db.Model):
    __tablename__ = 'pull_request_labels'
    __table_args__ = {"schema": "augur_data"}
    pr_label_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_labels_pull_requests_1',
                                                             ondelete="CASCADE", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_labels_repo',
                                                     ondelete="RESTRICT", onupdate="CASCADE"))
    pr_src_id = db.Column(db.BigInteger)
    pr_src_node_id = db.Column(db.String())
    pr_src_url = db.Column(db.String())
    pr_src_description = db.Column(db.String())
    pr_src_color = db.Column(db.String())
    pr_src_default_bool = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class PullRequestMessageRef(db.Model):
    __tablename__ = 'pull_request_message_ref'
    __table_args__ = {"schema": "augur_data"}
    pr_msg_ref_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_message_ref_pull_requests_1',
                                                             ondelete="RESTRICT", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pr_repo', ondelete="RESTRICT",
                                                     onupdate="CASCADE"))
    msg_id = db.Column(db.BigInteger,
                       db.ForeignKey('augur_data.message.msg_id', name='fk_pull_request_message_ref_message_1',
                                     ondelete="RESTRICT", onupdate="CASCADE"))
    pr_message_ref_src_comment_id = db.Column(db.BigInteger)
    pr_message_ref_src_node_id = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())
    pr_issue_url = db.Column(db.String())


class PullRequestMeta(db.Model):
    __tablename__ = 'pull_request_meta'
    __table_args__ = {"schema": "augur_data"}
    pr_repo_meta_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_meta_pull_requests_1',
                                                             ondelete="CASCADE", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_repo_meta_repo_id',
                                      ondelete="RESTRICT", onupdate="CASCADE"))
    pr_head_or_base = db.Column(db.String())
    pr_src_meta_label = db.Column(db.String())
    pr_src_meta_ref = db.Column(db.String())
    pr_sha = db.Column(db.String())
    cntrb_id = db.Column(db.BigInteger,
                         db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pull_request_meta_contributors_2'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("pr_meta-cntrbid-idx", PullRequestMeta.cntrb_id.asc().nullslast())


class PullRequestRepo(db.Model):
    __tablename__ = 'pull_request_repo'
    __table_args__ = {"schema": "augur_data"}
    pr_repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pr_repo_meta_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_request_meta.pr_repo_meta_id',
                                                             name='fk_pull_request_repo_pull_request_meta_1',
                                                             ondelete="CASCADE", onupdate="CASCADE"))
    pr_repo_head_or_base = db.Column(db.String())
    pr_src_repo_id = db.Column(db.BigInteger)
    pr_src_node_id = db.Column(db.String())
    pr_repo_name = db.Column(db.String())
    pr_repo_full_name = db.Column(db.String())
    pr_repo_private_bool = db.Column(db.Boolean())
    pr_cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                                                         name='fk_pull_request_repo_contributors_1'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("pr-cntrb-idx-repo", PullRequestRepo.pr_cntrb_id.asc().nullslast())


class PullRequestReviewMessageRef(db.Model):
    __tablename__ = 'pull_request_review_message_ref'
    __table_args__ = {"schema": "augur_data"}
    pr_review_msg_ref_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pr_review_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_request_reviews.pr_review_id',
                                                          name='fk_pull_request_review_message_ref_pull_request_reviews_1',
                                                          ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_review_repo', ondelete="RESTRICT",
                                      onupdate="CASCADE"))
    msg_id = db.Column(db.BigInteger,
                       db.ForeignKey('augur_data.message.msg_id', name='fk_pull_request_review_message_ref_message_1',
                                     ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class PullRequestReviewers(db.Model):
    __tablename__ = 'pull_request_reviewers'
    __table_args__ = {"schema": "augur_data"}
    pr_reviewer_map_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_reviewers_pull_requests_1',
                                                             ondelete="CASCADE", onupdate="CASCADE"))
    pr_source_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                                                      name='fk_pull_request_reviewers_contributors_1',
                                                      ondelete="CASCADE", onupdate="CASCADE"))
    pr_reviewer_src_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("pr-reviewers-cntrb-idx1", PullRequestReviewers.cntrb_id.asc().nullslast())


class PullRequestReviews(db.Model):
    __tablename__ = 'pull_request_reviews'
    __table_args__ = {"schema": "augur_data"}
    pr_review_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_reviews_pull_requests_1',
                                                             ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_review', ondelete="RESTRICT",
                                      onupdate="CASCADE"))
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id',
                                                      name='fk_pull_request_reviews_contributors_1',
                                                      ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
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
                                                         ondelete="RESTRICT", onupdate="CASCADE"))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class PullRequestTeams(db.Model):
    __tablename__ = 'pull_request_teams'
    __table_args__ = {"schema": "augur_data"}
    pr_team_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id',
                                                             name='fk_pull_request_teams_pull_requests_1',
                                                             ondelete="CASCADE", onupdate="CASCADE"))
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class Pull_Requests(db.Model):
    __tablename__ = 'pull_requests'
    __table_args__ = {"schema": "augur_data"}
    pull_request_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger,
                        db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_requests_repo_1', ondelete="CASCADE",
                                      onupdate="CASCADE"))
    pr_url = db.Column(db.String())
    pr_src_id = db.Column(db.BigInteger)
    pr_src_node_id = db.Column(db.String())
    pr_html_url = db.Column(db.String())
    pr_diff_url = db.Column(db.String())
    pr_patch_url = db.Column(db.String())
    pr_issue_url = db.Column(db.String())
    pr_augur_issue_id = db.Column(db.BigInteger)
    pr_src_number = db.Column(db.BigInteger)
    pr_src_state = db.Column(db.String())
    pr_src_locked = db.Column(db.Boolean())
    pr_src_title = db.Column(db.String())
    pr_augur_contributor_id = db.Column(db.BigInteger,
                                        db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pr_contribs',
                                                      ondelete="RESTRICT", onupdate="CASCADE"))
    pr_body = db.Column(db.Text())
    pr_created_at = db.Column(db.TIMESTAMP())
    pr_updated_at = db.Column(db.TIMESTAMP())
    pr_closed_at = db.Column(db.TIMESTAMP())
    pr_merged_at = db.Column(db.TIMESTAMP())
    pr_merge_commit_sha = db.Column(db.String())
    pr_teams = db.Column(db.BigInteger)
    pr_milestone = db.Column(db.String())
    pr_commits_url = db.Column(db.String())
    pr_review_comments_url = db.Column(db.String())
    pr_review_comment_url = db.Column(db.String())
    pr_comments_url = db.Column(db.String())
    pr_statuses_url = db.Column(db.String())
    pr_meta_head_id = db.Column(db.String())
    pr_meta_base_id = db.Column(db.String())
    pr_src_issue_url = db.Column(db.String())
    pr_src_comments_url = db.Column(db.String())
    pr_src_review_comments_url = db.Column(db.String())
    pr_src_commits_url = db.Column(db.String())
    pr_src_statuses_url = db.Column(db.String())
    pr_src_author_association = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("id_node", Pull_Requests.pr_src_id.desc().nullsfirst(),
      Pull_Requests.pr_src_node_id.desc().nullsfirst())
Index("pull_requests_idx_repo_id_data_datex", Pull_Requests.repo_id.asc().nullslast(),
      Pull_Requests.data_collection_date.asc().nullslast())


# TODO: Timestamps were declared with length of 6 in database
class Releases(db.Model):
    __tablename__ = 'releases'
    __table_args__ = {"schema": "augur_data"}
    release_id = db.Column(db.CHAR(length=64), primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_releases_repo_1'),
                        nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class Repo(db.Model):
    __tablename__ = 'repo'
    __table_args__ = {"schema": "augur_data"}
    repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_group_id = db.Column(db.BigInteger,
                              db.ForeignKey('augur_data.repo_groups.repo_group_id', name='fk_repo_repo_groups_1'),
                              nullable=False)
    repo_git = db.Column(db.String(), nullable=False)
    repo_path = db.Column(db.String())
    repo_name = db.Column(db.String())
    repo_added = db.Column(db.TIMESTAMP(), nullable=False, default=datetime.now())
    repo_status = db.Column(db.String(), nullable=False)
    repo_type = db.Column(db.String())
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("forked", Repo.forked_from.asc().nullslast())
Index("repo_idx_repo_id_repo_namex", Repo.repo_id.asc().nullslast(), Repo.repo_name.asc().nullslast())
Index("repogitindexrep", Repo.repo_git.asc().nullslast())

Index("reponameindex", Repo.repo_name, postgresql_using='hash')

Index("reponameindexbtree", Repo.repo_name.asc().nullslast())
Index("rggrouponrepoindex", Repo.repo_group_id.asc().nullslast())
Index("therepo", Repo.repo_id.asc().nullslast(), unique=True)


class RepoBadging(db.Model):
    __tablename__ = 'repo_badging'
    __table_args__ = {"schema": "augur_data"}
    badge_collection_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_badging_repo_1'))
    created_at = db.Column(db.TIMESTAMP(), default=datetime.now())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())
    data = db.Column(postgresql.JSONB())


class RepoClusterMessages(db.Model):
    __tablename__ = 'repo_cluster_messages'
    __table_args__ = {"schema": "augur_data"}
    msg_cluster_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_cluster_messages_repo_1'))
    cluster_content = db.Column(db.Integer)
    cluster_mechanism = db.Column(db.Integer)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class RepoDependencies(db.Model):
    __tablename__ = 'repo_dependencies'
    __table_args__ = {"schema": "augur_data"}
    repo_dependencies_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='repo_id'))
    dep_name = db.Column(db.String())
    dep_count = db.Column(db.Integer)
    dep_language = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


# TODO: typo in field current_verion
class RepoDepsLibyear(db.Model):
    __tablename__ = 'repo_deps_libyear'
    __table_args__ = {"schema": "augur_data"}
    repo_deps_libyear_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='repo_id_copy_2'))
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class RepoDepsScorecard(db.Model):
    __tablename__ = 'repo_deps_scorecard'
    __table_args__ = {"schema": "augur_data"}
    repo_deps_scorecard_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='repo_id_copy_1'))
    name = db.Column(db.String())
    status = db.Column(db.String())
    score = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class RepoGroupInsights(db.Model):
    __tablename__ = 'repo_group_insights'
    __table_args__ = {"schema": "augur_data"}
    rgi_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_group_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo_groups.repo_group_id',
                                                           name='fk_repo_group_insights_repo_groups_1'))
    rgi_metric = db.Column(db.String())
    rgi_value = db.Column(db.String())
    cms_id = db.Column(db.BigInteger)
    rgi_fresh = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


# TODO: Has varchar with length but changed here
class RepoGroups(db.Model):
    __tablename__ = 'repo_groups'
    __table_args__ = {"schema": "augur_data"}
    repo_group_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    rg_name = db.Column(db.String(), nullable=False)
    rg_description = db.Column(db.String())
    rg_website = db.Column(db.String())
    rg_recache = db.Column(db.SmallInteger)
    rg_last_modified = db.Column(db.TIMESTAMP(), nullable=False)
    rg_type = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("rgidm", RepoGroups.repo_group_id.asc().nullslast(), unique=True)
Index("rgnameindex", RepoGroups.rg_name.asc().nullslast())


# TODO: has varchar with length, but changed here
class RepoGroupsListServe(db.Model):
    __tablename__ = 'repo_groups_list_serve'
    __table_args__ = {"schema": "augur_data"}
    rgls_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_group_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo_groups.repo_group_id',
                                                           name='fk_repo_groups_list_serve_repo_groups_1')
    nullable = False)
    rgls_name = db.Column(db.String())
    rgls_description = db.Column(db.String())
    rgls_sponsor = db.Column(db.String())
    rgls_email = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("lister", RepoGroupsListServe.rgls_id.asc().nullslast(), RepoGroupsListServe.repo_group_id.asc().nullslast(),
      unique=True)


class RepoInfo(db.Model):
    __tablename__ = 'repo_info'
    __table_args__ = {"schema": "augur_data"}
    repo_info_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_info_repo_1'),
                        nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())

    # TODO: Their appears to be two of the same index in current database


Index("repo_info_idx_repo_id_data_date_1x", RepoInfo.repo_id.asc().nullslast(),
      RepoInfo.data_collection_date.asc().nullslast())


# TODO: Why is numeric defined without level or precision?
class RepoInsights(db.Model):
    __tablename__ = 'repo_insights'
    __table_args__ = {"schema": "augur_data"}
    ri_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_insights_repo_1'))
    ri_metric = db.Column(db.String())
    ri_value = db.Column(db.String())
    ri_date = db.Column(db.TIMESTAMP())
    ri_fresh = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())
    ri_score = db.Column(db.Numeric())
    ri_field = db.Column(db.String())
    ri_detection_method = db.Column(db.String())


class RepoInsightsRecords(db.Model):
    __tablename__ = 'repo_insights_records'
    __table_args__ = {"schema": "augur_data"}
    ri_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='repo_id_ref', ondelete="SET NULL",
                                                     onupdate="CASCADE"))
    ri_metric = db.Column(db.String())
    ri_field = db.Column(db.String())
    ri_value = db.Column(db.String())
    ri_date = db.Column(db.TIMESTAMP())
    ri_score = db.Column(db.Float())
    ri_detection_method = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("dater", RepoInsightsRecords.ri_date.asc().nullslast())


class RepoLabor(db.Model):
    __tablename__ = 'repo_labor'
    __table_args__ = {"schema": "augur_data"}
    repo_labor_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_labor_repo_1'))
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
    repo_url = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class RepoMeta(db.Model):
    __tablename__ = 'repo_meta'
    __table_args__ = {"schema": "augur_data"}
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_meta_repo_1'),
                        primary_key=True, nullable=False)
    rmeta_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    rmeta_name = db.Column(db.String())
    rmeta_value = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class RepoSbomScans(db.Model):
    __tablename__ = 'repo_sbom_scans'
    __table_args__ = {"schema": "augur_data"}
    rsb_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.Integer,
                        db.ForeignKey('augur_data.repo.repo_id', name='repo_linker_sbom', ondelete="CASCADE",
                                      onupdate="CASCADE"))
    sbom_scan = db.Column(db.JSON())


class RepoStats(db.Model):
    __tablename__ = 'repo_stats'
    __table_args__ = {"schema": "augur_data"}
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_stats_repo_1'),
                        primary_key=True, nullable=False)
    rstat_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    rstat_name = db.Column(db.String())
    rstat_value = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class RepoTestCoverage(db.Model):
    __tablename__ = 'repo_test_coverage'
    __table_args__ = {"schema": "augur_data"}
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_test_coverage_repo_1'),
                        primary_key=True, nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


class RepoTopic(db.Model):
    __tablename__ = 'repo_topic'
    __table_args__ = {"schema": "augur_data"}
    repo_topic_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.Integer, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_topic_repo_1'))
    topic_id = db.Column(db.Integer)
    topic_prob = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


# TODO: Added primary keys
class ReposFetchLog(db.Model):
    __tablename__ = 'repos_fetch_log'
    __table_args__ = {"schema": "augur_data"}
    repos_id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.String(), primary_key=True, nullable=False)
    date = db.Column(db.TIMESTAMP(), nullable=False)


# TODO: There appear to be two identical indexes
Index("repos_id,status", ReposFetchLog.repos_id.asc().nullslast(),
      ReposFetchLog.status.asc().nullslast())


# TODO: Has varchar with length but I changed here
class Settings(db.Model):
    __tablename__ = 'settings'
    __table_args__ = {"schema": "augur_data"}
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    setting = db.Column(db.String(), nullable=False)
    value = db.Column(db.String(), nullable=False)
    last_modified = db.Column(db.TIMESTAMP(), nullable=False)


class TopicWords(db.Model):
    __tablename__ = 'topic_words'
    __table_args__ = {"schema": "augur_data"}
    topic_words_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    topic_id = db.Column(db.BigInteger)
    word = db.Column(db.String())
    word_prob = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


# TODO: Defined a primary key of all the non null and default values
class UnknownCache(db.Model):
    __tablename__ = 'unknown_cache'
    __table_args__ = {"schema": "augur_data"}
    type = db.Column(db.String(), primary_key=True, nullable=False)
    repo_group_id = db.Column(db.Integer, primary_key=True, nullable=False)
    email = db.Column(db.String(), primary_key=True, nullable=False)
    domain = db.Column(db.String())
    added = db.Column(db.BigInteger, primary_key=True, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


Index("type,projects_id", UnknownCache.type.asc().nullslast(),
      UnknownCache.repo_group_id.asc().nullslast())


class UnresolvedCommitEmails(db.Model):
    __tablename__ = 'unresolved_commit_emails'
    __table_args__ = {"schema": "augur_data"}
    email_unresolved_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    name = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), default=datetime.now())


# TODO: Has varchar with length but changed it
class UtilityLog(db.Model):
    __tablename__ = 'utility_log'
    __table_args__ = {"schema": "augur_data"}
    id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    level = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False)
    attempted = db.Column(db.TIMESTAMP(), nullable=False)


# TODO: Needed to define a primary key
class WorkingCommits(db.Model):
    __tablename__ = 'working_commits'
    __table_args__ = {"schema": "augur_data"}
    repos_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    working_commit = db.Column(db.String())


if __name__ == '__main__':
    app.run(debug=True)






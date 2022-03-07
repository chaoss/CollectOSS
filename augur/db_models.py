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
# TODO: How to define primary key without autoincrement
# TODO: Why to some values have default set to NULL then their data type if they will default to NULL anyway

# TODO: removed asc and dsc from hash indexes because they are not supported (it automatically set them to ASC NULLS LAST which is the same as all the ones in the database)
# TODO: Foreign keys should also be not null to make it more clear a row can't be added without it


# TODO: Why is there a working_commits and repos_fetch_log in both of the schemas? There classes conflict 


# TODO: Added primary key
class AnalysisLog(db.Model):
    analysis_log_id = db.Column(db.BigInteger, primary_key=True)
    repos_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(), nullable=False)
    date_attempted = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

    __tablename__ = 'analysis_log'
    __table_args__ = (
        db.Index("repos_id", repos_id),
        {"schema":"augur_data"}
    )

class ChaossMetricStatus(db.Model):
    __tablename__ = 'chaoss_metric_status'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": "This table used to track CHAOSS Metric implementations in Augur, but due to the constantly changing location of that information, it is for the moment not actively populated. "}
    )
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    cm_working_group_focus_area = db.Column(db.String())


class CommitCommentRef(db.Model):
    __tablename__ = 'commit_comment_ref'
    __table_args__ = (
        UniqueConstraint('cmt_comment_src_id', name='commitcomment'),
        {"schema": "augur_data"}
    )
    cmt_comment_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cmt_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.commits.cmt_id', name='fk_commit_comment_ref_commits_1', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    repo_id = db.Column(db.BigInteger)
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_commit_comment_ref_message_1', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    user_id = db.Column(db.BigInteger, nullable=False)
    body = db.Column(db.Text())
    line = db.Column(db.BigInteger)
    position = db.Column(db.BigInteger)
    commit_comment_src_node_id = db.Column(db.String())
    cmt_comment_src_id = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

    

Index("comment_id", CommitCommentRef.cmt_comment_src_id.asc().nullslast(), CommitCommentRef.cmt_comment_id.asc().nullslast(), CommitCommentRef.msg_id.asc().nullslast())

    
class CommitParents(db.Model):
    cmt_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.commits.cmt_id', name='fk_commit_parents_commits_1'), primary_key=True)
    parent_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.commits.cmt_id', name='fk_commit_parents_commits_2'), primary_key=True)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'commit_parents'
    __table_args__ = (
        db.Index("commit_parents_ibfk_1", cmt_id),
        db.Index("commit_parents_ibfk_2", parent_id),
        {"schema":"augur_data"}
    )



# TODO: Current db version has some varchar defined with length but I changed that with flask
# TODO: Add foriegn key: cmt_author_platform_username = db.Column(db.String(), db.ForeignKey('augur_data.contributors.cntrb_login', name='fk_commits_contributors_3', ondelete="CASCADE", onupdate="CASCADE"))
class Commits(db.Model):
    cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_commits_repo_2', ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

    __tablename__ = 'commits'
    __table_args__ = (
        db.Index("author_affiliation", cmt_author_affiliation, postgresql_using='hash'),
        db.Index("author_cntrb_id", cmt_ght_author_id),
        db.Index("author_email,author_affiliation,author_date", cmt_author_email, cmt_author_affiliation, cmt_author_date),
        db.Index("author_raw_email", cmt_author_raw_email),
        db.Index("cmt-author-date-idx2", cmt_author_date),
        db.Index("cmt_author_contrib_worker", cmt_author_name, cmt_author_email, cmt_author_date, postgresql_using='brin'),
        db.Index("cmt_commiter_contrib_worker", cmt_committer_name, cmt_committer_email, cmt_committer_date, postgresql_using='brin'),
        db.Index("commited", cmt_id),
        db.Index("commits_idx_cmt_email_cmt_date_cmt_name", cmt_author_email, cmt_author_date, cmt_author_name),
        db.Index("commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam", repo_id, cmt_author_email, cmt_author_date, cmt_author_name),
        db.Index("commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam2", repo_id, cmt_committer_email, cmt_committer_date, cmt_committer_name),
        db.Index("committer_affiliation", cmt_committer_affiliation, postgresql_using='hash'),
        db.Index("committer_email,committer_affiliation,committer_date", cmt_committer_email, cmt_committer_affiliation, cmt_committer_date),
        db.Index("committer_raw_email", cmt_committer_raw_email),
        db.Index("repo_id,commit", repo_id, cmt_commit_hash),
        {
            "schema":"augur_data",
            "comment":"Commits.\nEach row represents changes to one FILE within a single commit. So you will encounter multiple rows per commit hash in many cases. "
        }
    )

# TODO: Set default for ca_start_date to '1970-01-01'
# TODO: Set default for ca_active to 1
# Current db has varchar with length but I changed that
class ContributorAffiliations(db.Model):
    __tablename__ = 'contributor_affiliations'
    __table_args__ = (
        UniqueConstraint('ca_domain', name='unique_domain'), 
        {"schema":"augur_data",
        "comment": "This table exists outside of relations with other tables. The purpose is to provide a dynamic, owner maintained (and augur augmented) list of affiliations. This table is processed in affiliation information in the DM_ tables generated when Augur is finished counting commits using the Facade Worker. "}
    )
    ca_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    ca_domain = db.Column(db.String(), nullable=False)
    ca_start_date = db.Column(db.Date, server_default='1970-01-01')
    ca_last_used = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())
    ca_affiliation = db.Column(db.String())
    ca_active = db.Column(db.SmallInteger, server_default=text('1'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

    


class ContributorRepo(db.Model):
    __tablename__ = 'contributor_repo'
    __table_args__ = (
        PrimaryKeyConstraint('cntrb_repo_id', name='cntrb_repo_id_key'), 
        UniqueConstraint('event_id', 'tool_version', name='eventer'),
        {"schema":"augur_data"}
    )
    cntrb_repo_id = db.Column(db.BigInteger, nullable=False)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_contributor_repo_contributors_1', ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    repo_git = db.Column(db.String(), nullable=False)
    repo_name = db.Column(db.String(), nullable=False)
    gh_repo_id = db.Column(db.BigInteger, nullable=False)
    cntrb_category = db.Column(db.String())
    event_id = db.Column(db.BigInteger)
    created_at = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())



# TODO: Set cntrb_fake default to 0
# TODO: Set cntrb_deleted default to 0
class Contributors(db.Model):
    __tablename__ = 'contributors'
    __table_args__ = (
        UniqueConstraint('gh_login', name='GH-UNIQUE-C', initially="DEFERRED", deferrable=True),
        UniqueConstraint('gl_id', name='GL-UNIQUE-B', initially="DEFERRED", deferrable=True),
        UniqueConstraint('gl_username', name='GL-UNIQUE-C', initially="DEFERRED", deferrable=True),
        UniqueConstraint('cntrb_login', name='GL-cntrb-LOGIN-UNIQUE'), 
        {"schema":"augur_data",
        "comment": "For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login.\nGithub now allows a user to change their login name, but their user id remains the same in this case. So, the natural key is the combination of id and login, but there should never be repeated logins. "}
    )
    cntrb_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cntrb_login = db.Column(db.String())
    cntrb_email = db.Column(db.String())
    cntrb_full_name = db.Column(db.String())
    cntrb_company = db.Column(db.String())
    cntrb_created_at = db.Column(db.TIMESTAMP())
    cntrb_type = db.Column(db.String())
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("cnt-fullname", Contributors.cntrb_full_name, postgresql_using='hash')
Index("cntrb-theemail", Contributors.cntrb_email, postgresql_using='hash')

Index("cntrb_canonica-idx11", Contributors.cntrb_canonical.asc().nullslast())
Index("cntrb_login_platform_index", Contributors.cntrb_login.asc().nullslast())

Index("contributor_delete_finder", Contributors.cntrb_id, Contributors.cntrb_email, postgresql_using='brin')
Index("contributor_worker_email_finder", Contributors.cntrb_email, postgresql_using='brin')
Index("contributor_worker_finder", Contributors.cntrb_login, Contributors.cntrb_email, Contributors.cntrb_id, postgresql_using='brin')

# TODO: This index is the saem as the first one but one has a different stuff
Index("contributor_worker_fullname_finder", Contributors.cntrb_full_name, postgresql_using='brin')

Index("contributors_idx_cntrb_email3", Contributors.cntrb_email.asc().nullslast())

# TODO: These last onese appear to be the same
Index("login", Contributors.cntrb_login.asc().nullslast())
Index("login-contributor-idx", Contributors.cntrb_login.asc().nullslast())


 


class ContributorsAliases(db.Model):
    __tablename__ = 'contributors_aliases'
    __table_args__ = (
        UniqueConstraint('alias_email', 'canonical_email', name='only-email-once', initially="DEFERRED", deferrable=True), 
        {"schema":"augur_data",
        "comment": 'Every open source user may have more than one email used to make contributions over time. Augur selects the first email it encounters for a user as its “canonical_email”. \n\nThe canonical_email is also added to the contributors_aliases table, with the canonical_email and alias_email being identical.  Using this strategy, an email search will only need to join the alias table for basic email information, and can then more easily map the canonical email from each alias row to the same, more detailed information in the contributors table for a user. '}
    )
    cntrb_alias_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_contributors_aliases_contributors_1', ondelete="CASCADE", onupdate="CASCADE", initially="DEFERRED", deferrable=True), nullable=False)
    canonical_email = db.Column(db.String(), nullable=False)
    alias_email = db.Column(db.String(), nullable=False)
    cntrb_active = db.Column(db.SmallInteger, nullable=False, server_default=text('1'))
    cntrb_last_modified = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())




# TODO: msg_id should be not null since foreign key
class DiscourseInsights(db.Model):
    __tablename__ = 'discourse_insights'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": "This table is populated by the “Discourse_Analysis_Worker”. It examines sequential discourse, using computational linguistic methods, to draw statistical inferences regarding the discourse in a particular comment thread. "}
    )
    msg_discourse_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_discourse_insights_message_1'))
    discourse_act = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO Temporaily defined priimary key on first attribute so it would generate
class DmRepoAnnual(db.Model):
    __tablename__ = 'dm_repo_annual'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("repo_id,affiliation_copy_1", DmRepoAnnual.repo_id.asc().nullslast(), DmRepoAnnual.affiliation.asc().nullslast())
Index("repo_id,email_copy_1", DmRepoAnnual.repo_id.asc().nullslast(), DmRepoAnnual.email.asc().nullslast())


class DmRepoGroupAnnual(db.Model):
    __tablename__ = 'dm_repo_group_annual'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("projects_id,affiliation_copy_1", DmRepoGroupAnnual.repo_group_id.asc().nullslast(), DmRepoGroupAnnual.affiliation.asc().nullslast())
Index("projects_id,email_copy_1", DmRepoGroupAnnual.repo_group_id.asc().nullslast(), DmRepoGroupAnnual.email.asc().nullslast())


class DmRepoGroupMonthly(db.Model):
    __tablename__ = 'dm_repo_group_monthly'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("projects_id,affiliation_copy_2", DmRepoGroupMonthly.repo_group_id.asc().nullslast(), DmRepoGroupMonthly.affiliation.asc().nullslast())
Index("projects_id,email_copy_2", DmRepoGroupMonthly.repo_group_id.asc().nullslast(), DmRepoGroupMonthly.email.asc().nullslast())
Index("projects_id,year,affiliation_copy_1", DmRepoGroupMonthly.repo_group_id.asc().nullslast(), DmRepoGroupMonthly.year.asc().nullslast(), DmRepoGroupMonthly.affiliation.asc().nullslast())
Index("projects_id,year,email_copy_1", DmRepoGroupMonthly.repo_group_id.asc().nullslast(), DmRepoGroupMonthly.year.asc().nullslast(), DmRepoGroupMonthly.email.asc().nullslast())


class DmRepoGroupWeekly(db.Model):
    __tablename__ = 'dm_repo_group_weekly'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("projects_id,affiliation", DmRepoGroupWeekly.repo_group_id.asc().nullslast(), DmRepoGroupWeekly.affiliation.asc().nullslast())
Index("projects_id,email", DmRepoGroupWeekly.repo_group_id.asc().nullslast(), DmRepoGroupWeekly.email.asc().nullslast())
Index("projects_id,year,affiliation", DmRepoGroupWeekly.repo_group_id.asc().nullslast(), DmRepoGroupWeekly.year.asc().nullslast(), DmRepoGroupWeekly.affiliation.asc().nullslast())
Index("projects_id,year,email", DmRepoGroupWeekly.repo_group_id.asc().nullslast(), DmRepoGroupWeekly.year.asc().nullslast(), DmRepoGroupWeekly.email.asc().nullslast())

class DmRepoMonthly(db.Model):
    __tablename__ = 'dm_repo_monthly'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("repo_id,affiliation_copy_2", DmRepoMonthly.repo_id.asc().nullslast(), DmRepoMonthly.affiliation.asc().nullslast())
Index("repo_id,email_copy_2", DmRepoMonthly.repo_id.asc().nullslast(), DmRepoMonthly.email.asc().nullslast())
Index("repo_id,year,affiliation_copy_1", DmRepoMonthly.repo_id.asc().nullslast(), DmRepoMonthly.year.asc().nullslast(), DmRepoMonthly.affiliation.asc().nullslast())
Index("repo_id,year,email_copy_1", DmRepoMonthly.repo_id.asc().nullslast(), DmRepoMonthly.year.asc().nullslast(), DmRepoMonthly.email.asc().nullslast())


class DmRepoWeekly(db.Model):
    __tablename__ = 'dm_repo_weekly'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("repo_id,affiliation", DmRepoWeekly.repo_id.asc().nullslast(), DmRepoWeekly.affiliation.asc().nullslast())
Index("repo_id,email", DmRepoWeekly.repo_id.asc().nullslast(), DmRepoWeekly.email.asc().nullslast())
Index("repo_id,year,affiliation", DmRepoWeekly.repo_id.asc().nullslast(), DmRepoWeekly.year.asc().nullslast(), DmRepoWeekly.affiliation.asc().nullslast())
Index("repo_id,year,email", DmRepoWeekly.repo_id.asc().nullslast(), DmRepoWeekly.year.asc().nullslast(), DmRepoWeekly.email.asc().nullslast())

class Exclude(db.Model):
    __tablename__ = 'exclude'
    __table_args__ = ({"schema":"augur_data"})
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    projects_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(), server_default='NULL')
    domain = db.Column(db.String(), server_default='NULL')


class IssueAssignees(db.Model):
    __tablename__ = 'issue_assignees'
    __table_args__ = ({"schema":"augur_data"})
    issue_assignee_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.issues.issue_id', name='fk_issue_assignees_issues_1'))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_issue_assignee_repo_id', ondelete="RESTRICT", onupdate="CASCADE"))
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_issue_assignees_contributors_1'))
    issue_assignee_src_id = db.Column(db.BigInteger)
    issue_assignee_src_node = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("issue-cntrb-assign-idx-1", IssueAssignees.cntrb_id.asc().nullslast())


class IssueEvents(db.Model):
    __tablename__ = 'issue_events'
    __table_args__ = (
        UniqueConstraint('issue_id', 'issue_event_src_id', name='unique_event_id_key'), 
        {"schema":"augur_data"}
    )
    event_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.issues.issue_id', name='fk_issue_events_issues_1', ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_issue_events_repo', ondelete="RESTRICT", onupdate="CASCADE"))
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_issue_events_contributors_1', ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    action = db.Column(db.String(), nullable=False)
    action_commit_hash = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())
    node_id = db.Column(db.String())
    node_url = db.Column(db.String())
    issue_event_src_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    platform_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.platform.pltfrm_id', name='fk_issue_event_platform_ide', ondelete="RESTRICT", onupdate="CASCADE"))

Index("issue-cntrb-idx2", IssueEvents.issue_event_src_id.asc().nullslast())
Index("issue_events_ibfk_1", IssueEvents.issue_id.asc().nullslast())
Index("issue_events_ibfk_2", IssueEvents.cntrb_id.asc().nullslast())




class IssueLabels(db.Model):
    __tablename__ = 'issue_labels'
    __table_args__ = (
        UniqueConstraint('label_src_id', 'issue_id', name='unique_issue_label'), 
        {"schema":"augur_data"}
    )
    issue_label_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.issues.issue_id', name='fk_issue_labels_issues_1'))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_issue_labels_repo_id', ondelete="RESTRICT", onupdate="CASCADE"))
    label_text = db.Column(db.String())
    label_description = db.Column(db.String())
    label_color = db.Column(db.String())
    label_src_id = db.Column(db.BigInteger)
    label_src_node_id = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())




class IssueMessageRef(db.Model):
    __tablename__ = 'issue_message_ref'
    __table_args__ = (
        UniqueConstraint('issue_msg_ref_src_comment_id', 'tool_source', name='repo-issue'),
        {"schema":"augur_data"}
    )
    issue_msg_ref_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.issues.issue_id', name='fk_issue_message_ref_issues_1', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_id_fk1', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_issue_message_ref_message_1', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    issue_msg_ref_src_node_id = db.Column(db.String())
    issue_msg_ref_src_comment_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# should repo_id be allowed to be NULL?
class Issues(db.Model):
    __tablename__ = 'issues'
    __table_args__ = ({"schema":"augur_data"})
    issue_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_issues_repo', ondelete="CASCADE", onupdate="CASCADE"))
    reporter_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_issues_contributors_2'))
    pull_request = db.Column(db.BigInteger)
    pull_request_id = db.Column(db.BigInteger)
    created_at = db.Column(db.TIMESTAMP())
    issue_title = db.Column(db.String())
    issue_body = db.Column(db.String())
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_issues_contributors_1'))
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("issue-cntrb-dix2", Issues.cntrb_id.asc().nullslast())
Index("issues_ibfk_1", Issues.repo_id.asc().nullslast())
Index("issues_ibfk_2", Issues.reporter_id.asc().nullslast())
Index("issues_ibfk_4", Issues.pull_request_id.asc().nullslast())


# TODO: Should latest_release_timestamp be a timestamp
# TODO: I made data_collection_date have a default it doesn't in current db
class Libraries(db.Model):
    __tablename__ = 'libraries'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO: I made data_collection_date have a default it doesn't in current db
class LibraryDependecies(db.Model):
    __tablename__ = 'library_dependencies'
    __table_args__ = ({"schema":"augur_data"})
    lib_dependency_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    library_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.libraries.library_id', name='fk_library_dependencies_libraries_1'))
    manifest_platform = db.Column(db.String())
    manifest_filepath = db.Column(db.String())
    manifest_kind = db.Column(db.String())
    repo_id_branch = db.Column(db.String(), nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("REPO_DEP", LibraryDependecies.library_id.asc().nullslast())


# TODO: I made data_collection_date have a default it doesn't in current db
class LibraryVersion(db.Model):
    __tablename__ = 'library_version'
    __table_args__ = ({"schema":"augur_data"})
    library_version_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    library_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.libraries.library_id', name='fk_library_version_libraries_1'))
    library_platform = db.Column(db.String())
    version_number = db.Column(db.String())
    version_release_date = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class LstmAnomalyModels(db.Model):
    __tablename__ = 'lstm_anomaly_models'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class LstmAnomalyResults(db.Model):
    __tablename__ = 'lstm_anomaly_results'
    __table_args__ = ({"schema":"augur_data"})
    result_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_lstm_anomaly_results_repo_1'))
    repo_category = db.Column(db.String())
    model_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.lstm_anomaly_models.model_id', name='fk_lstm_anomaly_results_lstm_anomaly_models_1'))
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class Message(db.Model):
    __tablename__ = 'message'
    __table_args__ = (
        UniqueConstraint('platform_msg_id', 'tool_source', name='gh-message'), 
        {"schema":"augur_data"}
    )
    msg_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    rgls_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo_groups_list_serve.rgls_id', name='fk_message_repo_groups_list_serve_1', ondelete="CASCADE", onupdate="CASCADE"))
    platform_msg_id = db.Column(db.BigInteger)
    platform_node_id = db.Column(db.String())
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_message_repoid', ondelete="CASCADE", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_message_contributors_1', ondelete="CASCADE", onupdate="CASCADE"))
    msg_text = db.Column(db.String())
    msg_timestamp = db.Column(db.TIMESTAMP())
    msg_sender_email = db.Column(db.String())
    msg_header = db.Column(db.String())
    pltfrm_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.platform.pltfrm_id', name='fk_message_platform_1', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("messagegrouper", Message.msg_id.asc().nullslast(), 
    Message.rgls_id.asc().nullslast(), unique=True)
Index("msg-cntrb-id-idx", Message.cntrb_id.asc().nullslast())
Index("platformgrouper", Message.msg_id.asc().nullslast(), 
    Message.pltfrm_id.asc().nullslast())


class MessageAnalysis(db.Model):
    __tablename__ = 'message_analysis'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class MessageAnalysisSummary(db.Model):
    __tablename__ = 'message_analysis_summary'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": "In a relationally perfect world, we would have a table called “message_analysis_run” the incremented the “worker_run_id” for both message_analysis and message_analysis_summary. For now, we decided this was overkill. "}
    )
    msg_summary_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_message_analysis_summary_repo_1'))
    worker_run_id = db.Column(db.BigInteger)
    positive_ratio = db.Column(db.Float())
    negative_ratio = db.Column(db.Float())
    novel_count = db.Column(db.BigInteger)
    period = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class MessageSentiment(db.Model):
    __tablename__ = 'message_sentiment'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class MessageSentimentSummary(db.Model):
    __tablename__ = 'message_sentiment_summary'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": "In a relationally perfect world, we would have a table called “message_sentiment_run” the incremented the “worker_run_id” for both message_sentiment and message_sentiment_summary. For now, we decided this was overkill. "}
    )
    msg_summary_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_message_sentiment_summary_repo_1'))
    worker_run_id = db.Column(db.BigInteger)
    positive_ratio = db.Column(db.Float())
    negative_ratio = db.Column(db.Float())
    novel_count = db.Column(db.BigInteger)
    period = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO: I made data_collection_date have a default it doesn't in current db
class Platform(db.Model):
    __tablename__ = 'platform'
    __table_args__ = (
        PrimaryKeyConstraint('pltfrm_id', name='theplat'),
        {"schema":"augur_data"}
    )
    pltfrm_id = db.Column(db.BigInteger, nullable=False)
    pltfrm_name = db.Column(db.String())
    pltfrm_version = db.Column(db.String())
    pltfrm_release_date = db.Column(db.Date)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("plat", Platform.pltfrm_id.asc().nullslast(), unique=True)


class PullRequestAnalysis(db.Model):
    __tablename__ = 'pull_request_analysis'
    __table_args__ = ({"schema":"augur_data"})
    pull_request_analysis_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_analysis_pull_requests_1', ondelete="CASCADE", onupdate="CASCADE"))
    merge_probability = db.Column(db.Numeric(precision=256, scale=250))
    mechanism = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

Index("pr_anal_idx", PullRequestAnalysis.pull_request_id.asc().nullslast())
Index("probability_idx", PullRequestAnalysis.merge_probability.desc().nullslast())


class PullRequestAssignees(db.Model):
    __tablename__ = 'pull_request_assignees'
    __table_args__ = ({"schema":"augur_data"})
    pr_assignee_map_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_assignees_pull_requests_1'))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_assignees_repo_id', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    contrib_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pull_request_assignees_contributors_1'))
    pr_assignee_src_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("pr_meta_cntrb-idx", PullRequestAssignees.contrib_id.asc().nullslast())


class PullRequestCommits(db.Model):
    __tablename__ = 'pull_request_commits'
    __table_args__ = (
        UniqueConstraint('pull_request_id', 'repo_id', 'pr_cmt_sha', name='pr_commit_nk'),
        {"schema":"augur_data",
        "comment": "Pull request commits are an enumeration of each commit associated with a pull request. \nNot all pull requests are from a branch or fork into master. \nThe commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).\nTherefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. \nIn cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. "}
    )
    pr_cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_commits_pull_requests_1', ondelete="CASCADE", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_commits_repo_id', ondelete="RESTRICT", onupdate="CASCADE"))
    pr_cmt_sha = db.Column(db.String())
    pr_cmt_node_id = db.Column(db.String())
    pr_cmt_message = db.Column(db.String())
    #TODO: varbit in database can't find sqlalchemy equivalent
    pr_cmt_comments_url = db.Column(db.LargeBinary())
    pr_cmt_author_cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pr_commit_cntrb_id', ondelete="CASCADE", onupdate="CASCADE"))
    pr_cmt_timestamp = db.Column(db.TIMESTAMP())
    pr_cmt_author_email = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO: Set default platform_id to be 25150
class PullRequestEvents(db.Model):
    __tablename__ = 'pull_request_events'
    __table_args__ = (
        PrimaryKeyConstraint('pr_event_id', name='pr_events_pkey'),
        UniqueConstraint('pr_platform_event_id', 'platform_id', name='unique-pr-event-id'),
        {"schema":"augur_data"}
    )
    pr_event_id = db.Column(db.BigInteger, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_events_pull_requests_1', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fkprevent_repo_id', ondelete="RESTRICT", onupdate="RESTRICT", initially="DEFERRED", deferrable=True))
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pull_request_events_contributors_1'), nullable=False)
    action = db.Column(db.String(), nullable=False)
    action_commit_hash = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())
    issue_event_src_id = db.Column(db.BigInteger)
    node_id = db.Column(db.String())
    node_url = db.Column(db.String())
    platform_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.platform.pltfrm_id', name='fkpr_platform', ondelete="RESTRICT", onupdate="RESTRICT", initially="DEFERRED", deferrable=True),server_default=text('25150'))
    pr_platform_event_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("pr_events_ibfk_1", PullRequestEvents.pull_request_id.asc().nullslast())
Index("pr_events_ibfk_2", PullRequestEvents.cntrb_id.asc().nullslast())


class PullRequestFiles(db.Model):
    __tablename__ = 'pull_request_files'
    __table_args__ = (
        UniqueConstraint('pull_request_id', 'repo_id', 'pr_file_path', name='prfiles_unique'),
        {"schema":"augur_data",
        "comment": "Pull request commits are an enumeration of each commit associated with a pull request. \nNot all pull requests are from a branch or fork into master. \nThe commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).\nTherefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. \nIn cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. "}
    )
    pr_file_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_commits_pull_requests_1_copy_1', ondelete="CASCADE", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_files_repo_id', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    pr_file_additions = db.Column(db.BigInteger)
    pr_file_deletions = db.Column(db.BigInteger)
    pr_file_path = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class PullRequestLabels(db.Model):
    __tablename__ = 'pull_request_labels'
    __table_args__ = (
        UniqueConstraint('pr_src_id', 'pull_request_id', name='unique-pr-src-label-id'),
        {"schema":"augur_data"}
    )
    pr_label_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_labels_pull_requests_1', ondelete="CASCADE", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_labels_repo', ondelete="RESTRICT", onupdate="CASCADE"))
    pr_src_id = db.Column(db.BigInteger)
    pr_src_node_id = db.Column(db.String())
    pr_src_url = db.Column(db.String())
    pr_src_description = db.Column(db.String())
    pr_src_color = db.Column(db.String())
    pr_src_default_bool = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class PullRequestMessageRef(db.Model):
    __tablename__ = 'pull_request_message_ref'
    __table_args__ = (
        UniqueConstraint('pr_message_ref_src_comment_id', 'tool_source', name='pr-comment-nk'),
        {"schema":"augur_data"}
    )
    pr_msg_ref_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_message_ref_pull_requests_1', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pr_repo', ondelete="RESTRICT", onupdate="CASCADE"))
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_pull_request_message_ref_message_1', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    pr_message_ref_src_comment_id = db.Column(db.BigInteger)
    pr_message_ref_src_node_id = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    pr_issue_url = db.Column(db.String())


class PullRequestMeta(db.Model):
    __tablename__ = 'pull_request_meta'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": 'Pull requests contain referencing metadata.  There are a few columns that are discrete. There are also head and base designations for the repo on each side of the pull request. Similar functions exist in GitLab, though the language here is based on GitHub. The JSON Being adapted to as of the development of this schema is here:      "base": {       "label": "chaoss:dev",       "ref": "dev",       "sha": "dc6c6f3947f7dc84ecba3d8bda641ef786e7027d",       "user": {         "login": "chaoss",         "id": 29740296,         "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",         "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",         "gravatar_id": "",         "url": "https://api.github.com/users/chaoss",         "html_url": "https://github.com/chaoss",         "followers_url": "https://api.github.com/users/chaoss/followers",         "following_url": "https://api.github.com/users/chaoss/following{/other_user}",         "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",         "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",         "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",         "organizations_url": "https://api.github.com/users/chaoss/orgs",         "repos_url": "https://api.github.com/users/chaoss/repos",         "events_url": "https://api.github.com/users/chaoss/events{/privacy}",         "received_events_url": "https://api.github.com/users/chaoss/received_events",         "type": "Organization",         "site_admin": false       },       "repo": {         "id": 78134122,         "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",         "name": "augur",         "full_name": "chaoss/augur",         "private": false,         "owner": {           "login": "chaoss",           "id": 29740296,           "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",           "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",           "gravatar_id": "",           "url": "https://api.github.com/users/chaoss",           "html_url": "https://github.com/chaoss",           "followers_url": "https://api.github.com/users/chaoss/followers",           "following_url": "https://api.github.com/users/chaoss/following{/other_user}",           "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",           "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",           "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",           "organizations_url": "https://api.github.com/users/chaoss/orgs",           "repos_url": "https://api.github.com/users/chaoss/repos",           "events_url": "https://api.github.com/users/chaoss/events{/privacy}",           "received_events_url": "https://api.github.com/users/chaoss/received_events",           "type": "Organization",           "site_admin": false         }, '}
    )
    pr_repo_meta_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_meta_pull_requests_1', ondelete="CASCADE", onupdate="CASCADE"))
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_request_repo_meta_repo_id', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    pr_head_or_base = db.Column(db.String())
    pr_src_meta_label = db.Column(db.String())
    pr_src_meta_ref = db.Column(db.String())
    pr_sha = db.Column(db.String())
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pull_request_meta_contributors_2'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("pr_meta-cntrbid-idx", PullRequestMeta.cntrb_id.asc().nullslast())


class PullRequestRepo(db.Model):
    __tablename__ = 'pull_request_repo'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": "This table is for storing information about forks that exist as part of a pull request. Generally we do not want to track these like ordinary repositories. "}
    )
    pr_repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pr_repo_meta_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_request_meta.pr_repo_meta_id', name='fk_pull_request_repo_pull_request_meta_1', ondelete="CASCADE", onupdate="CASCADE"))
    pr_repo_head_or_base = db.Column(db.String())
    pr_src_repo_id = db.Column(db.BigInteger)
    pr_src_node_id = db.Column(db.String())
    pr_repo_name = db.Column(db.String())
    pr_repo_full_name = db.Column(db.String())
    pr_repo_private_bool = db.Column(db.Boolean())
    pr_cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pull_request_repo_contributors_1'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("pr-cntrb-idx-repo", PullRequestRepo.pr_cntrb_id.asc().nullslast())


class PullRequestReviewMessageRef(db.Model):
    __tablename__ = 'pull_request_review_message_ref'
    __table_args__ = (
        PrimaryKeyConstraint('pr_review_msg_ref_id', name='pr_review_msg_ref_id'),
        UniqueConstraint('pr_review_msg_src_id', 'tool_source', name='pr-review-nk'),
        {"schema":"augur_data"}
    )
    pr_review_msg_ref_id = db.Column(db.BigInteger, nullable=False)
    pr_review_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_request_reviews.pr_review_id', name='fk_pull_request_review_message_ref_pull_request_reviews_1', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True), nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_review_repo', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True))
    msg_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.message.msg_id', name='fk_pull_request_review_message_ref_message_1', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True), nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class PullRequestReviewers(db.Model):
    __tablename__ = 'pull_request_reviewers'
    __table_args__ = (
        UniqueConstraint('pr_source_id', 'pr_reviewer_src_id', name='unique_pr_src_reviewer_key', initially="DEFERRED", deferrable=True),
        {"schema":"augur_data"}
    )
    pr_reviewer_map_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_reviewers_pull_requests_1', ondelete="CASCADE", onupdate="CASCADE"))
    pr_source_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pull_request_reviewers_contributors_1', ondelete="CASCADE", onupdate="CASCADE"))
    pr_reviewer_src_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("pr-reviewers-cntrb-idx1", PullRequestReviewers.cntrb_id.asc().nullslast())


# TODO: Set default platform_id to be 25150
class PullRequestReviews(db.Model):
    __tablename__ = 'pull_request_reviews'
    __table_args__ = (
        PrimaryKeyConstraint('pr_review_id', name='pull_request_review_id'),
        UniqueConstraint('pr_review_src_id', 'tool_source', name='sourcepr-review-id'),
        {"schema":"augur_data"}
    )
    pr_review_id = db.Column(db.BigInteger, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_reviews_pull_requests_1', ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_review', ondelete="RESTRICT", onupdate="CASCADE"))
    cntrb_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pull_request_reviews_contributors_1', ondelete="RESTRICT", onupdate="CASCADE"), nullable=False)
    pr_review_author_association = db.Column(db.String())
    pr_review_state = db.Column(db.String())
    pr_review_body = db.Column(db.String())
    pr_review_submitted_at = db.Column(db.TIMESTAMP())
    pr_review_src_id = db.Column(db.BigInteger)
    pr_review_node_id = db.Column(db.String())
    pr_review_html_url = db.Column(db.String())
    pr_review_pull_request_url = db.Column(db.String())
    pr_review_commit_id = db.Column(db.String())
    platform_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.platform.pltfrm_id', name='fk-review-platform', ondelete="RESTRICT", onupdate="CASCADE", initially="DEFERRED", deferrable=True), server_default=text('25150'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class PullRequestTeams(db.Model):
    __tablename__ = 'pull_request_teams'
    __table_args__ = ({"schema":"augur_data"})
    pr_team_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.pull_requests.pull_request_id', name='fk_pull_request_teams_pull_requests_1', ondelete="CASCADE", onupdate="CASCADE"))
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class Pull_Requests(db.Model):
    __tablename__ = 'pull_requests'
    __table_args__ = ({"schema":"augur_data"})
    pull_request_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_pull_requests_repo_1', ondelete="CASCADE", onupdate="CASCADE"), server_default=text('0'))
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
    pr_augur_contributor_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.contributors.cntrb_id', name='fk_pr_contribs', ondelete="RESTRICT", onupdate="CASCADE"))
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("id_node", Pull_Requests.pr_src_id.desc().nullsfirst(), 
    Pull_Requests.pr_src_node_id.desc().nullsfirst())
Index("pull_requests_idx_repo_id_data_datex", Pull_Requests.repo_id.asc().nullslast(),
    Pull_Requests.data_collection_date.asc().nullslast())


# TODO: Timestamps were declared with length of 6 in database
class Releases(db.Model):
    __tablename__ = 'releases'
    __table_args__ = ({"schema":"augur_data"})
    release_id = db.Column(db.CHAR(length=64), primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_releases_repo_1'), nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO: I made data_collection_date have a default it doesn't in current db
class Repo(db.Model):
    __tablename__ = 'repo'
    __table_args__ = (
        PrimaryKeyConstraint('repo_id', name='repounique'),
        {"schema":"augur_data",
        "comment": "This table is a combination of the columns in Facade’s repo table and GHTorrent’s projects table. "}
    )
    repo_id = db.Column(db.BigInteger, nullable=False)
    repo_group_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo_groups.repo_group_id', name='fk_repo_repo_groups_1'), nullable=False)
    repo_git = db.Column(db.String(), nullable=False)
    repo_path = db.Column(db.String(), server_default='NULL')
    repo_name = db.Column(db.String(), server_default='NULL')
    repo_added = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())
    repo_status = db.Column(db.String(), nullable=False, server_default='New')
    repo_type = db.Column(db.String(), server_default='')
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("forked", Repo.forked_from.asc().nullslast())
Index("repo_idx_repo_id_repo_namex", Repo.repo_id.asc().nullslast(), Repo.repo_name.asc().nullslast())
Index("repogitindexrep", Repo.repo_git.asc().nullslast())

Index("reponameindex", Repo.repo_name, postgresql_using='hash')

Index("reponameindexbtree", Repo.repo_name.asc().nullslast())
Index("rggrouponrepoindex", Repo.repo_group_id.asc().nullslast())
Index("therepo", Repo.repo_id.asc().nullslast(), unique=True)

class RepoBadging(db.Model):
    __tablename__ = 'repo_badging'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": 'This will be collected from the LF’s Badging API\nhttps://bestpractices.coreinfrastructure.org/projects.json?pq=https%3A%2F%2Fgithub.com%2Fchaoss%2Faugur\n'}
    )
    badge_collection_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_badging_repo_1'))
    created_at = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    data = db.Column(JSONB())


class RepoClusterMessages(db.Model):
    __tablename__ = 'repo_cluster_messages'
    __table_args__ = ({"schema":"augur_data"})
    msg_cluster_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_cluster_messages_repo_1'))
    cluster_content = db.Column(db.Integer)
    cluster_mechanism = db.Column(db.Integer)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class RepoDependencies(db.Model):
    __tablename__ = 'repo_dependencies'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": "Contains the dependencies for a repo."}
    )
    repo_dependencies_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='repo_id'))
    dep_name = db.Column(db.String())
    dep_count = db.Column(db.Integer)
    dep_language = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO: typo in field current_verion
class RepoDepsLibyear(db.Model):
    __tablename__ = 'repo_deps_libyear'
    __table_args__ = ({"schema":"augur_data"})
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class RepoDepsScorecard(db.Model):
    __tablename__ = 'repo_deps_scorecard'
    __table_args__ = (
        PrimaryKeyConstraint('repo_deps_scorecard_id', name='repo_deps_scorecard_pkey1'),
        {"schema":"augur_data"}
    )
    repo_deps_scorecard_id = db.Column(db.BigInteger, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='repo_id_copy_1'))
    name = db.Column(db.String())
    status = db.Column(db.String())
    score = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class RepoGroupInsights(db.Model):
    __tablename__ = 'repo_group_insights'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a REPOSITORY_GROUP and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. \n\nWorker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. '}
    )
    rgi_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_group_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo_groups.repo_group_id', name='fk_repo_group_insights_repo_groups_1'))
    rgi_metric = db.Column(db.String())
    rgi_value = db.Column(db.String())
    cms_id = db.Column(db.BigInteger)
    rgi_fresh = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO: Has varchar with length but changed here
# TODO: I made data_collection_date have a default it doesn't in current db
class RepoGroups(db.Model):
    __tablename__ = 'repo_groups'
    __table_args__ = (
        PrimaryKeyConstraint('repo_group_id', name='rgid'),
        {"schema":"augur_data",
        "comment": "rg_type is intended to be either a GitHub Organization or a User Created Repo Group. "}
    )
    repo_group_id = db.Column(db.BigInteger, nullable=False)
    rg_name = db.Column(db.String(), nullable=False)
    rg_description = db.Column(db.String(), server_default='NULL')
    rg_website = db.Column(db.String(), server_default='NULL')
    rg_recache = db.Column(db.SmallInteger, server_default=text('1'))
    rg_last_modified = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())
    rg_type = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("rgidm", RepoGroups.repo_group_id.asc().nullslast(), unique=True)
Index("rgnameindex", RepoGroups.rg_name.asc().nullslast())


# TODO: has varchar with length, but changed here
# TODO: I made data_collection_date have a default it doesn't in current db
class RepoGroupsListServe(db.Model):
    __tablename__ = 'repo_groups_list_serve'
    __table_args__ = (
        UniqueConstraint('rgls_id', 'repo_group_id', name='rglistserve'),
        {"schema":"augur_data"}
    )
    rgls_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_group_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo_groups.repo_group_id', name='fk_repo_groups_list_serve_repo_groups_1'), nullable=False)
    rgls_name = db.Column(db.String())
    rgls_description = db.Column(db.String())
    rgls_sponsor = db.Column(db.String())
    rgls_email = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("lister", RepoGroupsListServe.rgls_id.asc().nullslast(), RepoGroupsListServe.repo_group_id.asc().nullslast(), unique=True)


class RepoInfo(db.Model):
    __tablename__ = 'repo_info'
    __table_args__ = ({"schema":"augur_data"})
    repo_info_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_info_repo_1'), nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

    # TODO: Their appears to be two of the same index in current database
Index("repo_info_idx_repo_id_data_date_1x", RepoInfo.repo_id.asc().nullslast(), 
    RepoInfo.data_collection_date.asc().nullslast())


# TODO: Why is numeric defined without level or precision?
class RepoInsights(db.Model):
    __tablename__ = 'repo_insights'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a repository and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. \n\nWorker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. '}
    )
    ri_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_insights_repo_1'))
    ri_metric = db.Column(db.String())
    ri_value = db.Column(db.String())
    ri_date = db.Column(db.TIMESTAMP())
    ri_fresh = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())
    ri_score = db.Column(db.Numeric())
    ri_field = db.Column(db.String())
    ri_detection_method = db.Column(db.String())


class RepoInsightsRecords(db.Model):
    __tablename__ = 'repo_insights_records'
    __table_args__ = ({"schema":"augur_data"})
    ri_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='repo_id_ref', ondelete="SET NULL", onupdate="CASCADE"))
    ri_metric = db.Column(db.String())
    ri_field = db.Column(db.String())
    ri_value = db.Column(db.String())
    ri_date = db.Column(db.TIMESTAMP())
    ri_score = db.Column(db.Float())
    ri_detection_method = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("dater", RepoInsightsRecords.ri_date.asc().nullslast())


# TODO: I made data_collection_date have a default it doesn't in current db
class RepoLabor(db.Model):
    __tablename__ = 'repo_labor'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": "repo_labor is a derivative of tables used to store scc code and complexity counting statistics that are inputs to labor analysis, which are components of CHAOSS value metric calculations. "}
    )
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO: I made data_collection_date have a default it doesn't in current db
class RepoMeta(db.Model):
    __tablename__ = 'repo_meta'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": "Project Languages"}
    )
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_meta_repo_1'), primary_key=True, nullable=False)
    rmeta_id = db.Column(db.BigInteger,  primary_key=True, nullable=False)
    rmeta_name = db.Column(db.String())
    rmeta_value = db.Column(db.String(), server_default=text('0'))
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class RepoSbomScans(db.Model):
    __tablename__ = 'repo_sbom_scans'
    __table_args__ = ({"schema":"augur_data"})
    rsb_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.Integer, db.ForeignKey('augur_data.repo.repo_id', name='repo_linker_sbom', ondelete="CASCADE", onupdate="CASCADE"))
    sbom_scan = db.Column(db.JSON())


# TODO: I made data_collection_date have a default it doesn't in current db
class RepoStats(db.Model):
    __tablename__ = 'repo_stats'
    __table_args__ = (
        {"schema":"augur_data",
        "comment": "Project Watchers"}
    )
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_stats_repo_1'), primary_key=True, nullable=False)
    rstat_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    rstat_name = db.Column(db.String())
    rstat_value = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class RepoTestCoverage(db.Model):
    __tablename__ = 'repo_test_coverage'
    __table_args__ = ({"schema":"augur_data"})
    repo_id = db.Column(db.BigInteger, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_test_coverage_repo_1'), primary_key=True, nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class RepoTopic(db.Model):
    __tablename__ = 'repo_topic'
    __table_args__ = ({"schema":"augur_data"})
    repo_topic_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.Integer, db.ForeignKey('augur_data.repo.repo_id', name='fk_repo_topic_repo_1'))
    topic_id = db.Column(db.Integer)
    topic_prob = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO: Added primary keys
class ReposFetchLog(db.Model):
    __tablename__ = 'repos_fetch_log'
    __table_args__ = ({"schema":"augur_data"})
    repos_fetch_log_id = db.Column(db.BigInteger, primary_key=True)
    repos_id = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(), nullable=False)
    date = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

# TODO: There appear to be two identical indexes
Index("repos_id,status", ReposFetchLog.repos_id.asc().nullslast(),
    ReposFetchLog.status.asc().nullslast())


# TODO: Has varchar with length but I changed here
class Settings(db.Model):
    __tablename__ = 'settings'
    __table_args__ = ({"schema":"augur_data"})
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    setting = db.Column(db.String(), nullable=False)
    value = db.Column(db.String(), nullable=False)
    last_modified = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())


class TopicWords(db.Model):
    __tablename__ = 'topic_words'
    __table_args__ = ({"schema":"augur_data"})
    topic_words_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    topic_id = db.Column(db.BigInteger)
    word = db.Column(db.String())
    word_prob = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


class UnknownCache(db.Model):
    __tablename__ = 'unknown_cache'
    __table_args__ = ({"schema":"augur_data"})
    unknown_cache_id = db.Column(db.BigInteger, primary_key=True)
    type = db.Column(db.String(), nullable=False)
    repo_group_id = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(), nullable=False)
    domain = db.Column(db.String(), server_default='NULL')
    added = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())

Index("type,projects_id", UnknownCache.type.asc().nullslast(), 
    UnknownCache.repo_group_id.asc().nullslast())


class UnresolvedCommitEmails(db.Model):
    __tablename__ = 'unresolved_commit_emails'
    __table_args__ = (
        UniqueConstraint('email', name='unresolved_commit_emails_email_key'),
        {"schema":"augur_data"}
    )
    email_unresolved_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    email = db.Column(db.String(), nullable=False)
    name = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# TODO: Has varchar with length but changed it
class UtilityLog(db.Model):
    __tablename__ = 'utility_log'
    __table_args__ = ({"schema":"augur_data"})
    id = db.Column(db.BigInteger, primary_key=True, nullable = False)
    level = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False)
    attempted = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())


# TODO: Needed to define a primary key
class WorkingCommits(db.Model):
    __tablename__ = 'working_commits'
    __table_args__ = ({"schema":"augur_data"})
    working_commits_id = db.Column(db.BigInteger, primary_key=True)
    repos_id = db.Column(db.Integer, nullable=False)
    working_commit = db.Column(db.String(), server_default='NULL')


# Start of Augur Operations tablespoon
class All(db.Model):
    __tablename__ = 'all'
    __table_args__ = ({"schema":"augur_operations"})
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


class AugurSettings(db.Model):
    __tablename__ = 'augur_settings'
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('setting', name='setting-unique'),
        {"schema":"augur_operations"}
    )
    id = db.Column(db.BigInteger)
    setting = db.Column(db.String())
    value = db.Column(db.String())
    last_modified = db.Column(db.TIMESTAMP(), server_default=func.current_timestamp())


# class ReposFetchLog(db.Model):
#     __tablename__ = 'repos_fetch_log'
#     __table_args__ = (
#         PrimaryKeyConstraint('repos_fetch_log_id'),
#         {"schema":"augur_operations"}
#     )
#     repos_fetch_log_id = db.Column(db.BigInteger)
#     repos_id = db.Column(db.Integer, nullable=False)
#     status = db.Column(db.String(), nullable=False)
#     date = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

# Index("repos_id,statusops", ReposFetchLog.repos_id.asc().nullslast(), ReposFetchLog.status.asc().nullslast())


class WorkerHistory(db.Model):
    __tablename__ = 'worker_history'
    __table_args__ = (
        PrimaryKeyConstraint('history_id', name='history_pkey'),
        {"schema":"augur_operations"}
    )
    history_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    worker = db.Column(db.String(), nullable=False)
    job_model = db.Column(db.String(), nullable=False)
    oauth_id = db.Column(db.Integer)
    timestamp = db.Column(db.TIMESTAMP(), nullable=False)
    status = db.Column(db.String(), nullable=False)
    total_results = db.Column(db.Integer)


class WorkerJob(db.Model):
    __tablename__ = 'worker_job'
    __table_args__ = (
        PrimaryKeyConstraint('job_model', name='job_pkey'),
        {"schema":"augur_operations"}
    )
    job_model = db.Column(db.String())
    state = db.Column(db.Integer, nullable=False, server_default=text('0'))
    zombie_head = db.Column(db.Integer)
    since_id_str = db.Column(db.String(), nullable=False, server_default='0')
    description = db.Column(db.String(), server_default='None')
    last_count = db.Column(db.Integer)
    last_run = db.Column(db.TIMESTAMP())
    analysis_state = db.Column(db.Integer, server_default=text('0'))
    oauth_id = db.Column(db.Integer, nullable=False)


class WorkerOauth(db.Model):
    __tablename__ = 'worker_oauth'
    __table_args__ = (
        PrimaryKeyConstraint('oauth_id'),
        {"schema":"augur_operations"}
    )
    oauth_id = db.Column(db.BigInteger)
    name = db.Column(db.String(), nullable=False)
    consumer_key = db.Column(db.String(), nullable=False)
    consumer_secret = db.Column(db.String(), nullable=False)
    access_token = db.Column(db.String(), nullable=False)
    access_token_secret = db.Column(db.String(), nullable=False)
    repo_directory = db.Column(db.String())
    platform = db.Column(db.String(), server_default='github')


class WorkerSettingsFacade(db.Model):
    __tablename__ = 'worker_settings_facade'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='settings_pkey'),
        {"schema":"augur_operations"}
    )
    id = db.Column(db.Integer)
    setting = db.Column(db.String(), nullable=False)
    value = db.Column(db.String(), nullable=False)
    last_modified = db.Column(db.TIMESTAMP(), nullable=False, server_default=func.current_timestamp())


# class WorkingCommits(db.Model):
#     __tablename__ = 'working_commits'
#     __table_args__ = (
#         PrimaryKeyConstraint('working_commits_id'),
#         {"schema":"augur_operations"}
#     )
#     working_commits_id = db.Column(db.BigInteger)
#     repos_id = db.Column(db.Integer, nullable=False)
#     working_commit = db.Column(db.String())
  

if __name__ == '__main__':
    app.run(debug=True)
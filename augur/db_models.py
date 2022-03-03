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

# TODO: Added primary key
class AnalysisLog(db.Model):
    __tablename__ = 'analysis_log'
    repos_id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.String(), primary_key=True, nullable=False)
    date_attempted = db.Column(db.TIMESTAMP(), nullable=False)


class ChaossMetricStatus(db.Model):
    __tablename__ = 'chaoss_metric_status'
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
    data_collection_date = db.Column(db.TIMESTAMP())
    cm_working_group_focus_area = db.Column(db.String())




class CommitCommentRef(db.Model):
    __tablename__ = 'commit_comment_ref'
    cmt_comment_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cmt_id = db.Column(db.BigInteger, nullable=False)
    repo_id = db.Column(db.BigInteger)
    msg_id = db.Column(db.BigInteger, nullable=False)
    user_id = db.Column(db.BigInteger, nullable=False)
    body = db.Column(db.Text())
    line = db.Column(db.BigInteger)
    position = db.Column(db.BigInteger)
    commit_comment_src_node_id = db.Column(db.String())
    cmt_comment_src_id = db.Column(db.BigInteger, nullable=False)
    created_at = db.Column(db.TIMESTAMP(), nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())


# TODO: Current db version has some varchar defined with length but I changed that with flask
# TODO: Also current db version has typos in data type definition of timestamps
class Commits(db.Model):
    __tablename__ = 'commits'
    cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, nullable=False)
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
    cmt_committer_timestamp = db.Column(db.TIMESTAMP())
    cmt_author_timestamp = db.Column(db.TIMESTAMP())
    cmt_author_platform_username = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

# Current db has varchar with length but I changed that
class ContributorAffiliations(db.Model):
    __tablename__ = 'contributor_affiliations'
    ca_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    ca_domain = db.Column(db.String(), nullable=False)
    ca_start_date = db.Column(db.Date)
    ca_last_used = db.Column(db.TIMESTAMP(), nullable=False)
    ca_affiliation = db.Column(db.String())
    ca_active = db.Column(db.SmallInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())


class ContributorRepo(db.Model):
    __tablename__ = 'contributor_repo'
    cntrb_repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cntrb_id = db.Column(db.BigInteger, nullable=False)
    repo_git = db.Column(db.String(), nullable=False)
    repo_name = db.Column(db.String(), nullable=False)
    gh_repo_id = db.Column(db.BigInteger, nullable=False)
    cntrb_category = db.Column(db.String())
    event_id = db.Column(db.BigInteger)
    created_at = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class Contributors(db.Model):
    __tablename__ = 'contributors'
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
    cntrb_last_used = db.Column(db.TIMESTAMP())
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
    data_collection_date = db.Column(db.TIMESTAMP())

class ContributorAliases(db.Model):
    __tablename__ = 'contributor_aliases'
    cntrb_alias_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cntrb_id = db.Column(db.BigInteger, nullable=False)
    canonical_email = db.Column(db.String(), nullable=False)
    alias_email = db.Column(db.String(), nullable=False)
    cntrb_active = db.Column(db.SmallInteger, nullable=False)
    cntrb_last_modified = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class IssueAssignees(db.Model):
    __tablename__ = 'issue_assignees'
    issue_assignee_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger)
    issue_assignee_src_id = db.Column(db.BigInteger)
    issue_assignee_src_node = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class IssueEvents(db.Model):
    __tablename__ = 'issue_events'
    event_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger, nullable=False)
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger, nullable=False)
    action = db.Column(db.String(), nullable=False)
    action_commit_hash = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP(), nullable=False)
    node_id = db.Column(db.String())
    node_url = db.Column(db.String())
    issue_event_src_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())
    platform_id = db.Column(db.BigInteger)

class IssueLabels(db.Model):
    __tablename__ = 'issue_labels'
    issue_label_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    label_text = db.Column(db.String())
    label_description = db.Column(db.String())
    label_color = db.Column(db.String())
    label_src_id = db.Column(db.BigInteger)
    label_src_node_id = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())


class IssueMessageRef(db.Model):
    __tablename__ = 'issue_message_ref'
    issue_msg_ref_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    issue_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    msg_id = db.Column(db.BigInteger)
    issue_msg_ref_src_node_id = db.Column(db.String())
    issue_msg_ref_src_comment_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

# should repo_id be allowed to be NULL?

class Issues(db.Model):
    __tablename__ = 'issues'
    issue_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger)
    reporter_id = db.Column(db.BigInteger)
    pull_request = db.Column(db.BigInteger)
    pull_request_id = db.Column(db.BigInteger)
    created_at = db.Column(db.TIMESTAMP())
    issue_title = db.Column(db.String())
    issue_body = db.Column(db.String())
    cntrb_id = db.Column(db.BigInteger)
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
    data_collection_date = db.Column(db.TIMESTAMP())

class Message(db.Model):
    __tablename__ = 'message'
    msg_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    rgls_id = db.Column(db.BigInteger)
    platform_msg_id = db.Column(db.BigInteger)
    platform_node_id = db.Column(db.String())
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger)
    msg_text = db.Column(db.String())
    msg_timestamp = db.Column(db.TIMESTAMP())
    msg_sender_email = db.Column(db.String())
    msg_header = db.Column(db.String())
    pltfrm_id = db.Column(db.BigInteger, nullable=False)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class MessageAnalysis(db.Model):
    __tablename__ = 'message_analysis'
    msg_analysis_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    msg_id = db.Column(db.BigInteger)
    worker_run_id = db.Column(db.BigInteger)
    sentiment_score = db.Column(db.Float())
    reconstruction_error = db.Column(db.Float())
    novelty_flag = db.Column(db.Boolean())
    feedback_flag = db.Column(db.Boolean())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class MessageAnalysisSummary(db.Model):
    __tablename__ = 'message_analysis_summary'
    msg_summary_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger)
    worker_run_id = db.Column(db.BigInteger)
    positive_ratio = db.Column(db.Float())
    negative_ratio = db.Column(db.Float())
    novel_count = db.Column(db.BigInteger)
    period = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class Platform(db.Model):
    __tablename__ = 'platform'
    pltfrm_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pltfrm_name = db.Column(db.String())
    pltfrm_version = db.Column(db.String())
    pltfrm_release_date = db.Column(db.Date)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())



class Pull_Requests(db.Model):
    __tablename__ = 'pull_requests'
    pull_request_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger)
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
    pr_augur_contributor_id = db.Column(db.BigInteger)
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
    data_collection_date = db.Column(db.TIMESTAMP())

class PullRequestCommits(db.Model):
    __tablename__ = 'pull_request_commits'
    pr_cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    pr_cmt_sha = db.Column(db.String())
    pr_cmt_node_id = db.Column(db.String())
    pr_cmt_message = db.Column(db.String())
    #TODO: varbit in database can't find sqlalchemy equivalent
    pr_cmt_comments_url = db.Column(db.String())
    pr_cmt_author_cntrb_id = db.Column(db.BigInteger)
    pr_cmt_timestamp = db.Column(db.TIMESTAMP())
    pr_cmt_author_email = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())


class PullRequestEvents(db.Model):
    __tablename__ = 'pull_request_events'
    pr_event_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger, nullable=False)
    repo_id = db.Column(db.BigInteger)
    cntrb_id = db.Column(db.BigInteger, nullable=False)
    action = db.Column(db.String(), nullable=False)
    action_commit_hash = db.Column(db.String())
    created_at = db.Column(db.TIMESTAMP(), nullable=False)
    issue_event_src_id = db.Column(db.BigInteger)
    node_id = db.Column(db.String())
    node_url = db.Column(db.String())
    platform_id = db.Column(db.BigInteger)
    pr_platform_event_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class PullRequestFiles(db.Model):
    __tablename__ = 'pull_request_files'
    pr_file_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    pr_file_additions = db.Column(db.BigInteger)
    pr_file_deletions = db.Column(db.BigInteger)
    pr_file_path = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class PullRequestLabels(db.Model):
    __tablename__ = 'pull_request_labels'
    pr_label_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP())

class PullRequestMeta(db.Model):
    __tablename__ = 'pull_request_meta'
    pr_repo_meta_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    pr_head_or_base = db.Column(db.String())
    pr_src_meta_label = db.Column(db.String())
    pr_src_meta_ref = db.Column(db.String())
    pr_sha = db.Column(db.String())
    cntrb_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class PullRequestMessageRef(db.Model):
    __tablename__ = 'pull_request_message_ref'
    pr_msg_ref_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.BigInteger)
    repo_id = db.Column(db.BigInteger)
    msg_id = db.Column(db.BigInteger)
    pr_message_ref_src_comment_id = db.Column(db.BigInteger)
    pr_message_ref_src_node_id = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())
    pr_issue_url = db.Column(db.String())

class PullRequestRepo(db.Model):
    __tablename__ = 'pull_request_repo'
    pr_repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pr_repo_meta_id = db.Column(db.BigInteger)
    pr_repo_head_or_base = db.Column(db.String())
    pr_src_repo_id = db.Column(db.BigInteger)
    pr_src_node_id = db.Column(db.String())
    pr_repo_name = db.Column(db.String())
    pr_repo_full_name = db.Column(db.String())
    pr_repo_private_bool = db.Column(db.Boolean())
    pr_cntrb_id = db.Column(db.BigInteger)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class PullRequestReviewMessageRef(db.Model):
    __tablename__ = 'pull_request_review_message_ref'
    pr_review_msg_ref_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    pr_review_id = db.Column(db.BigInteger, nullable=False)
    repo_id = db.Column(db.BigInteger)
    msg_id = db.Column(db.BigInteger, nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP())


# TODO: Timestamps were declared with length of 6 in database
class Releases(db.Model):
    __tablename__ = 'releases'
    release_id = db.Column(db.CHAR(length=64), primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP())

class Repo(db.Model):
    __tablename__ = 'repo'
    repo_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_group_id = db.Column(db.BigInteger, nullable=False)
    repo_git = db.Column(db.String(), nullable=False)
    repo_path = db.Column(db.String())
    repo_name = db.Column(db.String())
    repo_added = db.Column(db.TIMESTAMP(), nullable=False)
    repo_status = db.Column(db.String(), nullable=False)
    repo_type = db.Column(db.String())
    url = db.Column(db.String())
    owner_id = db.Column(db.Integer)
    description = db.Column(db.String())
    primary_language = db.Column(db.String())
    created_at = db.Column(db.String())
    forked_from = db.Column(db.String())
    updated_at = db.Column(db.TIMESTAMP())
    repo_archived_date_collected = db.Column(db.TIMESTAMP())
    repo_archived = db.Column(db.Integer)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

# TODO: Changed JSONB to JSON
class RepoBadging(db.Model):
    __tablename__ = 'repo_badging'
    badge_collection_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger)
    created_at = db.Column(db.TIMESTAMP())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())
    data = db.Column(db.JSON())

class RepoClusterMessages(db.Model):
    __tablename__ = 'repo_cluster_messages'
    msg_cluster_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger)
    cluster_content = db.Column(db.Integer)
    cluster_mechanism = db.Column(db.Integer)
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

# TODO: Has varchar with length but changed here
class RepoGroups(db.Model):
    __tablename__ = 'repo_groups'
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
    data_collection_date = db.Column(db.TIMESTAMP())

# TODO: has varchar with length, but changed here
class RepoGroupsListServe(db.Model):
    __tablename__ = 'repo_groups_list_serve'
    rgls_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_group_id = db.Column(db.BigInteger, nullable=False)
    rgls_name = db.Column(db.String())
    rgls_description = db.Column(db.String())
    rgls_sponsor = db.Column(db.String())
    rgls_email = db.Column(db.String())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

class RepoInfo(db.Model):
    __tablename__ = 'repo_info'
    repo_info_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger, nullable=False)
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
    data_collection_date = db.Column(db.TIMESTAMP())


class RepoLabor(db.Model):
    __tablename__ = 'repo_labor'
    repo_labor_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger)
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
    data_collection_date = db.Column(db.TIMESTAMP())

class RepoTopic(db.Model):
    __tablename__ = 'repo_topic'
    repo_topic_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.Integer)
    topic_id = db.Column(db.Integer)
    topic_prob = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

# TODO: Added primary keys
class ReposFetchLog(db.Model):
    __tablename__ = 'repos_fetch_log'
    repos_id = db.Column(db.Integer, primary_key=True, nullable=False)
    status = db.Column(db.String(), primary_key=True, nullable=False)
    date = db.Column(db.TIMESTAMP(), nullable=False)

# TODO: Has varchar with length but I changed here
class Settings(db.Model):
    __tablename__ = 'settings'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    setting = db.Column(db.String(), nullable=False)
    value = db.Column(db.String(), nullable=False)
    last_modified = db.Column(db.TIMESTAMP(), nullable=False)

class TopicWords(db.Model):
    __tablename__ = 'topic_words'
    topic_words_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    topic_id = db.Column(db.BigInteger)
    word = db.Column(db.String())
    word_prob = db.Column(db.Float())
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())

# TODO: Has varchar with length but changed it
class UtilityLog(db.Model):
    __tablename__ = 'utility_log'
    id = db.Column(db.BigInteger, primary_key=True, nullable = False)
    level = db.Column(db.String(), nullable=False)
    status = db.Column(db.String(), nullable=False)
    attempted = db.Column(db.TIMESTAMP(), nullable=False)


    # Template for model class
    """
    class Pull_Requests(db.Model):
    __tablename__ = 'pull_requests'
    pull_request_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger)
    pr_url = db.Column()
    pr_src_id = db.Column()
    pr_src_node_id = db.Column()
    pr_html_url = db.Column()
    pr_diff_url = db.Column()
    pr_patch_url = db.Column()
    pr_issue_url = db.Column()
    pr_augur_issue_id = db.Column()
    pr_src_number = db.Column()
    pr_src_state = db.Column()
    pr_src_locked = db.Column()
    pr_src_title = db.Column()
    pr_augur_contributor_id = db.Column()
    pr_body = db.Column()
    pr_created_at = db.Column()
    pr_updated_at = db.Column()
    pr_closed_at = db.Column()
    pr_merged_at = db.Column()
    pr_merge_commit_sha = db.Column()
    pr_teams = db.Column())
    pr_milestone = db.Column()
    pr_commits_url = db.Column()
    pr_review_comments_url = db.Column()
    pr_review_comment_url = db.Column()
    pr_comments_url = db.Column()
    pr_statuses_url = db.Column()
    pr_meta_head_id = db.Column()
    pr_meta_base_id = db.Column()
    pr_src_issue_url = db.Column()
    pr_src_comments_url = db.Column()
    pr_src_review_comments_url = db.Column()
    pr_src_commits_url = db.Column()
    pr_src_statuses_url = db.Column()
    pr_src_author_association = db.Column()
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())
    
class Pull_Requests(db.Model):
    __tablename__ = 'pull_requests'
    pull_request_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column(db.BigInteger)
    pr_url = db.Column()
    pr_src_id = db.Column()
    pr_src_node_id = db.Column()
    pr_html_url = db.Column()
    pr_diff_url = db.Column()
    pr_patch_url = db.Column()
    pr_issue_url = db.Column()
    pr_augur_issue_id = db.Column()
    pr_src_number = db.Column()
    pr_src_state = db.Column()
    pr_src_locked = db.Column()
    pr_src_title = db.Column()
    pr_augur_contributor_id = db.Column()
    pr_body = db.Column()
    pr_created_at = db.Column()
    pr_updated_at = db.Column()
    pr_closed_at = db.Column()
    pr_merged_at = db.Column()
    pr_src_issue_url = db.Column()
    pr_src_comments_url = db.Column()
    pr_src_review_comments_url = db.Column()
    pr_src_commits_url = db.Column()
    pr_src_statuses_url = db.Column()
    pr_src_author_association = db.Column()
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())
        
        
class Commits(db.Model):
    __tablename__ = 'commits'
    cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    repo_id = db.Column()
    cmt_commit_hash = db.Column()
    cmt_author_name = db.Column()
    cmt_author_raw_email = db.Column()
    cmt_author_affiliation = db.Column()
    cmt_committer_name = db.Column()
    cmt_committer_raw_email = db.Column()
    cmt_committer_email = db.Column()
    cmt_committer_date = db.Column()
    cmt_committer_affiliation = db.Column()
    cmt_added = db.Column()
    cmt_removed = db.Column()
    cmt_whitespace = db.Column()
    cmt_date_attempted = db.Column()
    cmt_ght_author_id = db.Column()
    cmt_author_platform_username = db.Column()
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())
        
class ContributorAliases(db.Model):
    __tablename__ = 'commits'
    cmt_id = db.Column(db.BigInteger, primary_key=True, nullable=False)
    cmt_commit_hash = db.Column()
    cmt_author_name = db.Column()
    cmt_author_raw_email = db.Column()
    cmt_author_affiliation = db.Column()
    cmt_committer_name = db.Column()
    cmt_author_platform_username = db.Column()
    tool_source = db.Column(db.String())
    tool_version = db.Column(db.String())
    data_source = db.Column(db.String())
    data_collection_date = db.Column(db.TIMESTAMP())
    """

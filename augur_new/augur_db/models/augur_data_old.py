# from augur.db.models.base import Base
# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     UniqueConstraint,
#     ForeignKey,
#     Text,
#     Boolean,
#     BigInteger,
#     SmallInteger,
#     Index,
#     Float,
#     func,
#     Date,
#     text,
#     Numeric,
#     PrimaryKeyConstraint,
#     CHAR,
#     TIMESTAMP,
#     JSON,
# )
# from sqlalchemy.dialects.postgresql import JSONB
# from sqlalchemy.orm import relationship

# # TODO: look at how facade queries it and add index

# # TODO: look at how facade queries it and add index
# class AnalysisLog(Base):
#     analysis_log_id = Column(BigInteger, primary_key=True)
#     repos_id = Column(Integer, nullable=False)
#     status = Column(String(), nullable=False)
#     date_attempted = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )

#     # this is an insert always table so it does not need a UniqueConstraint
#     __tablename__ = "analysis_log"
#     __table_args__ = (Index("repos_id", repos_id), {"schema": "augur_data"})


# # TODO: Manually filled by creation script
# # TODO: Could revive this table_


# class ChaossMetricStatus(Base):
#     cms_id = Column(BigInteger, primary_key=True, nullable=False)
#     cm_group = Column(String())
#     cm_source = Column(String())
#     cm_type = Column(String())
#     cm_backend_status = Column(String())
#     cm_frontend_status = Column(String())
#     cm_defined = Column(Boolean())
#     cm_api_endpoint_repo = Column(String())
#     cm_api_endpoint_rg = Column(String())
#     cm_name = Column(String())
#     cm_working_group = Column(String())
#     cm_info = Column(JSON())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())
#     cm_working_group_focus_area = Column(String())

#     __tablename__ = "chaoss_metric_status"
#     __table_args__ = {
#         "schema": "augur_data",
#         "comment": "This table used to track CHAOSS Metric implementations in Augur, but due to the constantly changing location of that information, it is for the moment not actively populated. ",
#     }


# class CommitCommentRef(Base):
#     cmt_comment_id = Column(BigInteger, primary_key=True, nullable=False)
#     cmt_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.commits.cmt_id",
#             name="fk_commit_comment_ref_commits_1",
#             onupdate="CASCADE",
#             ondelete="RESTRICT",
#         ),
#         nullable=False,
#     )
#     repo_id = Column(BigInteger)
#     msg_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.message.msg_id",
#             name="fk_commit_comment_ref_message_1",
#             onupdate="CASCADE",
#             ondelete="RESTRICT",
#         ),
#         nullable=False,
#     )
#     user_id = Column(BigInteger, nullable=False)
#     body = Column(Text())
#     line = Column(BigInteger)
#     position = Column(BigInteger)
#     commit_comment_src_node_id = Column(
#         String(),
#         comment="For data provenance, we store the source node ID if it exists. ",
#     )
#     cmt_comment_src_id = Column(
#         BigInteger,
#         nullable=False,
#         comment="For data provenance, we store the source ID if it exists. ",
#     )
#     created_at = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     message = relationship("Message", back_populates="commit")
#     commit = relationship("Commits", back_populates="msg_ref")

#     __tablename__ = "commit_comment_ref"
#     __table_args__ = (
#         Index("comment_id", cmt_comment_src_id, cmt_comment_id, msg_id),
#         # unique value for insertion
#         UniqueConstraint("cmt_comment_src_id", name="commitcomment"),
#         {"schema": "augur_data"},
#     )


# # TODO: This table does not get used so remove it and test without


# class CommitParents(Base):
#     cmt_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.commits.cmt_id", name="fk_commit_parents_commits_1"),
#         primary_key=True,
#     )
#     parent_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.commits.cmt_id", name="fk_commit_parents_commits_2"),
#         primary_key=True,
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "commit_parents"
#     __table_args__ = (
#         Index("commit_parents_ibfk_1", cmt_id),
#         Index("commit_parents_ibfk_2", parent_id),
#         {"schema": "augur_data"},
#     )


# # TODO: Add foriegn key: cmt_author_platform_username = Column(String(), ForeignKey('augur_data.contributors.cntrb_login', name='fk_commits_contributors_3', ondelete="CASCADE", onupdate="CASCADE"))
# # TODO: Add relationship with this foreign key
# class Commits(Base):
#     cmt_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_commits_repo_2",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#         nullable=False,
#     )
#     cmt_commit_hash = Column(String(), nullable=False)
#     cmt_author_name = Column(String(), nullable=False)
#     cmt_author_raw_email = Column(String(), nullable=False)
#     cmt_author_email = Column(String(), nullable=False)
#     cmt_author_date = Column(String(), nullable=False)
#     cmt_author_affiliation = Column(String(), server_default="NULL")
#     cmt_committer_name = Column(String(), nullable=False)
#     cmt_committer_raw_email = Column(String(), nullable=False)
#     cmt_committer_email = Column(String(), nullable=False)
#     cmt_committer_date = Column(String(), nullable=False)
#     cmt_committer_affiliation = Column(String(), server_default="NULL")
#     cmt_added = Column(Integer, nullable=False)
#     cmt_removed = Column(Integer, nullable=False)
#     cmt_whitespace = Column(Integer, nullable=False)
#     cmt_filename = Column(String(), nullable=False)
#     cmt_date_attempted = Column(TIMESTAMP(), nullable=False)
#     cmt_ght_author_id = Column(Integer)
#     cmt_ght_committer_id = Column(Integer)
#     cmt_ght_committed_at = Column(TIMESTAMP())
#     cmt_committer_timestamp = Column(TIMESTAMP(timezone=True))
#     cmt_author_timestamp = Column(TIMESTAMP(timezone=True))
#     # TODO: Appears that this foreign key is duplicated in the database
#     cmt_author_platform_username = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     msg_ref = relationship("CommitCommentRef", back_populates="commit")

#     def get_messages(self):

#         messages = []
#         for msg_ref in self.msg_ref:
#             messages.append(msg_ref.message)

#         return messages

#     __tablename__ = "commits"
#     __table_args__ = (
#         Index("author_affiliation", cmt_author_affiliation, postgresql_using="hash"),
#         Index("author_cntrb_id", cmt_ght_author_id),
#         Index(
#             "author_email,author_affiliation,author_date",
#             cmt_author_email,
#             cmt_author_affiliation,
#             cmt_author_date,
#         ),
#         Index("author_raw_email", cmt_author_raw_email),
#         Index("cmt-author-date-idx2", cmt_author_date),
#         Index(
#             "cmt_author_contrib_worker",
#             cmt_author_name,
#             cmt_author_email,
#             cmt_author_date,
#             postgresql_using="brin",
#         ),
#         Index(
#             "cmt_commiter_contrib_worker",
#             cmt_committer_name,
#             cmt_committer_email,
#             cmt_committer_date,
#             postgresql_using="brin",
#         ),
#         Index("commited", cmt_id),
#         Index(
#             "commits_idx_cmt_email_cmt_date_cmt_name",
#             cmt_author_email,
#             cmt_author_date,
#             cmt_author_name,
#         ),
#         Index(
#             "commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam",
#             repo_id,
#             cmt_author_email,
#             cmt_author_date,
#             cmt_author_name,
#         ),
#         Index(
#             "commits_idx_repo_id_cmt_ema_cmt_dat_cmt_nam2",
#             repo_id,
#             cmt_committer_email,
#             cmt_committer_date,
#             cmt_committer_name,
#         ),
#         Index(
#             "committer_affiliation", cmt_committer_affiliation, postgresql_using="hash"
#         ),
#         Index(
#             "committer_email,committer_affiliation,committer_date",
#             cmt_committer_email,
#             cmt_committer_affiliation,
#             cmt_committer_date,
#         ),
#         Index("committer_raw_email", cmt_committer_raw_email),
#         Index("repo_id,commit", repo_id, cmt_commit_hash),
#         {
#             "schema": "augur_data",
#             "comment": "Commits.\nEach row represents changes to one FILE within a single commit. So you will encounter multiple rows per commit hash in many cases. ",
#         },
#     )


# # Current has varchar with length but I changed that
# class ContributorAffiliations(Base):
#     ca_id = Column(BigInteger, primary_key=True, nullable=False)
#     ca_domain = Column(String(), nullable=False)
#     ca_start_date = Column(Date, server_default="1970-01-01")
#     ca_last_used = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )
#     ca_affiliation = Column(String())
#     ca_active = Column(SmallInteger, server_default=text("1"))
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "contributor_affiliations"
#     __table_args__ = (
#         UniqueConstraint("ca_domain", name="unique_domain"),
#         {
#             "schema": "augur_data",
#             "comment": "This table exists outside of relations with other tables. The purpose is to provide a dynamic, owner maintained (and augur augmented) list of affiliations. This table is processed in affiliation information in the DM_ tables generated when Augur is finished counting commits using the Facade Worker. ",
#         },
#     )


# # TODO: Add foreign key to repo table on cntrb_repo_id


# class ContributorRepo(Base):
#     cntrb_repo_id = Column(BigInteger, nullable=False)
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_contributor_repo_contributors_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#         nullable=False,
#         comment="This is not null because what is the point without the contributor in this table? ",
#     )
#     repo_git = Column(
#         String(),
#         nullable=False,
#         comment="Similar to cntrb_id, we need this data for the table to have meaningful data. ",
#     )
#     repo_name = Column(String(), nullable=False)
#     gh_repo_id = Column(BigInteger, nullable=False)
#     cntrb_category = Column(String())
#     event_id = Column(BigInteger)
#     created_at = Column(TIMESTAMP())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "contributor_repo"
#     __table_args__ = (
#         PrimaryKeyConstraint("cntrb_repo_id", name="cntrb_repo_id_key"),
#         UniqueConstraint("event_id", "tool_version", name="eventer"),
#         {"schema": "augur_data"},
#     )


# class Contributors(Base):
#     cntrb_id = Column(BigInteger, primary_key=True, nullable=False)
#     cntrb_login = Column(
#         String(),
#         comment="Will be a double population with the same value as gh_login for github, but the local value for other systems. ",
#     )
#     cntrb_email = Column(
#         String(),
#         comment="This needs to be here for matching contributor ids, which are augur, to the commit information. ",
#     )
#     cntrb_full_name = Column(String())
#     cntrb_company = Column(String())
#     cntrb_created_at = Column(TIMESTAMP())
#     cntrb_type = Column(
#         String(),
#         comment="Present in another models. It is not currently used in Augur. ",
#     )
#     cntrb_fake = Column(SmallInteger, server_default=text("0"))
#     cntrb_deleted = Column(SmallInteger, server_default=text("0"))
#     cntrb_long = Column(Numeric(precision=11, scale=8))
#     cntrb_lat = Column(Numeric(precision=10, scale=8))
#     cntrb_country_code = Column(CHAR(length=3))
#     cntrb_state = Column(String())
#     cntrb_city = Column(String())
#     cntrb_location = Column(String())
#     cntrb_canonical = Column(String())
#     cntrb_last_used = Column(TIMESTAMP(timezone=True))
#     gh_user_id = Column(BigInteger)
#     gh_login = Column(
#         String(),
#         comment="populated with the github user name for github originated data. ",
#     )
#     gh_url = Column(String())
#     gh_html_url = Column(String())
#     gh_node_id = Column(String())
#     gh_avatar_url = Column(String())
#     gh_gravatar_id = Column(String())
#     gh_followers_url = Column(String())
#     gh_following_url = Column(String())
#     gh_gists_url = Column(String())
#     gh_starred_url = Column(String())
#     gh_subscriptions_url = Column(String())
#     gh_organizations_url = Column(String())
#     gh_repos_url = Column(String())
#     gh_events_url = Column(String())
#     gh_received_events_url = Column(String())
#     gh_type = Column(String())
#     gh_site_admin = Column(String())
#     gl_web_url = Column(String())
#     gl_avatar_url = Column(String())
#     gl_state = Column(String())
#     gl_username = Column(String())
#     gl_full_name = Column(String())
#     gl_id = Column(BigInteger)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     repos_contributed = relationship("ContributorRepo")
#     aliases = relationship("ContributorsAliases")
#     messages = relationship("Message")

#     __tablename__ = "contributors"
#     __table_args__ = (
#         UniqueConstraint(
#             "gh_login", name="GH-UNIQUE-C", initially="DEFERRED", deferrable=True
#         ),
#         UniqueConstraint(
#             "gl_id", name="GL-UNIQUE-B", initially="DEFERRED", deferrable=True
#         ),
#         # unique key for gitlab users on insertion
#         UniqueConstraint(
#             "gl_username", name="GL-UNIQUE-C", initially="DEFERRED", deferrable=True
#         ),
#         # unique key to insert on for github
#         UniqueConstraint("cntrb_login", name="GL-cntrb-LOGIN-UNIQUE"),
#         Index("cnt-fullname", cntrb_full_name, postgresql_using="hash"),
#         Index("cntrb-theemail", cntrb_email, postgresql_using="hash"),
#         Index("cntrb_canonica-idx11", cntrb_canonical),
#         Index("cntrb_login_platform_index", cntrb_login),
#         Index(
#             "contributor_delete_finder", cntrb_id, cntrb_email, postgresql_using="brin"
#         ),
#         Index("contributor_worker_email_finder", cntrb_email, postgresql_using="brin"),
#         Index(
#             "contributor_worker_finder",
#             cntrb_login,
#             cntrb_email,
#             cntrb_id,
#             postgresql_using="brin",
#         ),
#         # TODO: This index is the same as the first one but one has a different stuff
#         Index(
#             "contributor_worker_fullname_finder",
#             cntrb_full_name,
#             postgresql_using="brin",
#         ),
#         Index("contributors_idx_cntrb_email3", cntrb_email),
#         # TODO: These last onese appear to be the same
#         Index("login", cntrb_login),
#         Index("login-contributor-idx", cntrb_login),
#         {
#             "schema": "augur_data",
#             "comment": "For GitHub, this should be repeated from gh_login. for other systems, it should be that systems login.\nGithub now allows a user to change their login name, but their user id remains the same in this case. So, the natural key is the combination of id and login, but there should never be repeated logins. ",
#         },
#     )


# class ContributorsAliases(Base):
#     cntrb_alias_id = Column(BigInteger, primary_key=True, nullable=False)
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_contributors_aliases_contributors_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#         nullable=False,
#     )
#     canonical_email = Column(String(), nullable=False)
#     alias_email = Column(String(), nullable=False)
#     cntrb_active = Column(SmallInteger, nullable=False, server_default=text("1"))
#     cntrb_last_modified = Column(TIMESTAMP(), server_default=func.current_timestamp())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "contributors_aliases"
#     __table_args__ = (
#         UniqueConstraint(
#             "alias_email",
#             "canonical_email",
#             name="only-email-once",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#         {
#             "schema": "augur_data",
#             "comment": "Every open source user may have more than one email used to make contributions over time. Augur selects the first email it encounters for a user as its “canonical_email”. \n\nThe canonical_email is also added to the contributors_aliases table, with the canonical_email and alias_email being identical.  Using this strategy, an email search will only need to join the alias table for basic email information, and can then more easily map the canonical email from each alias row to the same, more detailed information in the contributors table for a user. ",
#         },
#     )


# # TODO: Add relationship: Don't understand table well enough
# class DiscourseInsights(Base):
#     msg_discourse_id = Column(BigInteger, primary_key=True, nullable=False)
#     msg_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.message.msg_id", name="fk_discourse_insights_message_1"),
#     )
#     discourse_act = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "discourse_insights"
#     __table_args__ = {
#         "schema": "augur_data",
#         "comment": "This table is populated by the “Discourse_Analysis_Worker”. It examines sequential discourse, using computational linguistic methods, to draw statistical inferences regarding the discourse in a particular comment thread. ",
#     }


# # TODO: Add foreign keys to repo and repogroups


# class DmRepoAnnual(Base):
#     dm_repo_annual_id = Column(BigInteger, primary_key=True)
#     repo_id = Column(BigInteger, nullable=False)
#     email = Column(String(), nullable=False)
#     affiliation = Column(String(), server_default="NULL")
#     year = Column(SmallInteger, nullable=False)
#     added = Column(BigInteger, nullable=False)
#     removed = Column(BigInteger, nullable=False)
#     whitespace = Column(BigInteger, nullable=False)
#     files = Column(BigInteger, nullable=False)
#     patches = Column(BigInteger, nullable=False)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "dm_repo_annual"
#     __table_args__ = (
#         Index("repo_id,affiliation_copy_1", repo_id, affiliation),
#         Index("repo_id,email_copy_1", repo_id, email),
#         {"schema": "augur_data"},
#     )


# class DmRepoGroupAnnual(Base):
#     dm_repo_group_annual_id = Column(BigInteger, primary_key=True)
#     repo_group_id = Column(BigInteger, nullable=False)
#     email = Column(String(), nullable=False)
#     affiliation = Column(String(), server_default="NULL")
#     year = Column(SmallInteger, nullable=False)
#     added = Column(BigInteger, nullable=False)
#     removed = Column(BigInteger, nullable=False)
#     whitespace = Column(BigInteger, nullable=False)
#     files = Column(BigInteger, nullable=False)
#     patches = Column(BigInteger, nullable=False)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "dm_repo_group_annual"
#     __table_args__ = (
#         Index("projects_id,affiliation_copy_1", repo_group_id, affiliation),
#         Index("projects_id,email_copy_1", repo_group_id, email),
#         {"schema": "augur_data"},
#     )


# class DmRepoGroupMonthly(Base):
#     dm_repo_group_monthly_id = Column(BigInteger, primary_key=True)
#     repo_group_id = Column(BigInteger, nullable=False)
#     email = Column(String(), nullable=False)
#     affiliation = Column(String(), server_default="NULL")
#     month = Column(SmallInteger, nullable=False)
#     year = Column(SmallInteger, nullable=False)
#     added = Column(BigInteger, nullable=False)
#     removed = Column(BigInteger, nullable=False)
#     whitespace = Column(BigInteger, nullable=False)
#     files = Column(BigInteger, nullable=False)
#     patches = Column(BigInteger, nullable=False)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "dm_repo_group_monthly"
#     __table_args__ = (
#         Index("projects_id,affiliation_copy_2", repo_group_id, affiliation),
#         Index("projects_id,email_copy_2", repo_group_id, email),
#         Index("projects_id,year,affiliation_copy_1", repo_group_id, year, affiliation),
#         Index("projects_id,year,email_copy_1", repo_group_id, year, email),
#         {"schema": "augur_data"},
#     )


# class DmRepoGroupWeekly(Base):
#     dm_repo_group_weekly_id = Column(BigInteger, primary_key=True)
#     repo_group_id = Column(BigInteger, nullable=False)
#     email = Column(String(), nullable=False)
#     affiliation = Column(String(), server_default="NULL")
#     week = Column(SmallInteger, nullable=False)
#     year = Column(SmallInteger, nullable=False)
#     added = Column(BigInteger, nullable=False)
#     removed = Column(BigInteger, nullable=False)
#     whitespace = Column(BigInteger, nullable=False)
#     files = Column(BigInteger, nullable=False)
#     patches = Column(BigInteger, nullable=False)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "dm_repo_group_weekly"
#     __table_args__ = (
#         Index("projects_id,affiliation", repo_group_id, affiliation),
#         Index("projects_id,email", repo_group_id, email),
#         Index("projects_id,year,affiliation", repo_group_id, year, affiliation),
#         Index("projects_id,year,email", repo_group_id, year, email),
#         {"schema": "augur_data"},
#     )


# class DmRepoMonthly(Base):
#     dm_repo_monthly_id = Column(BigInteger, primary_key=True)
#     repo_id = Column(BigInteger, nullable=False)
#     email = Column(String(), nullable=False)
#     affiliation = Column(String(), server_default="NULL")
#     month = Column(SmallInteger, nullable=False)
#     year = Column(SmallInteger, nullable=False)
#     added = Column(BigInteger, nullable=False)
#     removed = Column(BigInteger, nullable=False)
#     whitespace = Column(BigInteger, nullable=False)
#     files = Column(BigInteger, nullable=False)
#     patches = Column(BigInteger, nullable=False)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "dm_repo_monthly"
#     __table_args__ = (
#         Index("repo_id,affiliation_copy_2", repo_id, affiliation),
#         Index("repo_id,email_copy_2", repo_id, email),
#         Index("repo_id,year,affiliation_copy_1", repo_id, year, affiliation),
#         Index("repo_id,year,email_copy_1", repo_id, year, email),
#         {"schema": "augur_data"},
#     )


# class DmRepoWeekly(Base):
#     dm_repo_weekly_id = Column(BigInteger, primary_key=True)
#     repo_id = Column(BigInteger, nullable=False)
#     email = Column(String(), nullable=False)
#     affiliation = Column(String(), server_default="NULL")
#     week = Column(SmallInteger, nullable=False)
#     year = Column(SmallInteger, nullable=False)
#     added = Column(BigInteger, nullable=False)
#     removed = Column(BigInteger, nullable=False)
#     whitespace = Column(BigInteger, nullable=False)
#     files = Column(BigInteger, nullable=False)
#     patches = Column(BigInteger, nullable=False)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "dm_repo_weekly"
#     __table_args__ = (
#         Index("repo_id,affiliation", repo_id, affiliation),
#         Index("repo_id,email", repo_id, email),
#         Index("repo_id,year,affiliation", repo_id, year, affiliation),
#         Index("repo_id,year,email", repo_id, year, email),
#         {"schema": "augur_data"},
#     )


# class Exclude(Base):
#     id = Column(Integer, primary_key=True, nullable=False)
#     projects_id = Column(Integer, nullable=False)
#     email = Column(String(), server_default="NULL")
#     domain = Column(String(), server_default="NULL")

#     __tablename__ = "exclude"
#     __table_args__ = {"schema": "augur_data"}


# # TODO: Add relationship for repo_id: I don't think the repo_id should be in this table, I think that behavior can be obtained by getting all the issues for a repo then all the issue assignees for those issues
# # TODO: Add relationship for cntrb_id
# class IssueAssignees(Base):
#     issue_assignee_id = Column(BigInteger, primary_key=True, nullable=False)
#     issue_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.issues.issue_id", name="fk_issue_assignees_issues_1"),
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_issue_assignee_repo_id",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#     )
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id", name="fk_issue_assignees_contributors_1"
#         ),
#     )
#     issue_assignee_src_id = Column(
#         BigInteger,
#         comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.",
#     )
#     issue_assignee_src_node = Column(
#         String(),
#         comment="This character based identifier comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API in the issue_assignees embedded JSON object. We may discover it is an ID for the person themselves; but my hypothesis is that its not.",
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "issue_assignees"
#     __table_args__ = (
#         Index("issue-cntrb-assign-idx-1", cntrb_id),
#         {"schema": "augur_data"},
#     )


# # TODO: Add relationship for repo_id: I don't think the repo_id should be in this table, I think that behavior can be obtained by getting all the issues for a repo then all the issue assignees for those issues
# # TODO: Add relationship for cntrb_id


# class IssueEvents(Base):
#     event_id = Column(BigInteger, primary_key=True, nullable=False)
#     issue_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.issues.issue_id",
#             name="fk_issue_events_issues_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#         nullable=False,
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_issue_events_repo",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#     )
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_issue_events_contributors_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#         nullable=False,
#     )
#     action = Column(String(), nullable=False)
#     action_commit_hash = Column(String())
#     created_at = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )
#     node_id = Column(
#         String(),
#         comment="This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.",
#     )
#     node_url = Column(String())
#     issue_event_src_id = Column(
#         BigInteger,
#         comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API",
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())
#     platform_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.platform.pltfrm_id",
#             name="fk_issue_event_platform_ide",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#     )

#     __tablename__ = "issue_events"
#     __table_args__ = (
#         # contstraint to determine whether to insert or not
#         UniqueConstraint("issue_id", "issue_event_src_id", name="unique_event_id_key"),
#         Index("issue-cntrb-idx2", issue_event_src_id),
#         Index("issue_events_ibfk_1", issue_id),
#         Index("issue_events_ibfk_2", cntrb_id),
#         {"schema": "augur_data"},
#     )


# # TODO: Add relationship for repo_id: I don't think the repo_id should be in this table, I think that behavior can be obtained by getting all the issues for a repo then all the issue assignees for those issues


# class IssueLabels(Base):
#     issue_label_id = Column(BigInteger, primary_key=True, nullable=False)
#     issue_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.issues.issue_id", name="fk_issue_labels_issues_1"),
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_issue_labels_repo_id",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#     )
#     label_text = Column(String())
#     label_description = Column(String())
#     label_color = Column(String())
#     label_src_id = Column(
#         BigInteger,
#         comment="This character based identifier (node) comes from the source. In the case of GitHub, it is the id that is the second field returned from the issue events API JSON subsection for issues.",
#     )
#     label_src_node_id = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "issue_labels"
#     __table_args__ = (
#         # insert on
#         UniqueConstraint("label_src_id", "issue_id", name="unique_issue_label"),
#         {"schema": "augur_data"},
#     )


# # TODO: Add replationship: for repo_id


# class IssueMessageRef(Base):
#     issue_msg_ref_id = Column(BigInteger, primary_key=True, nullable=False)
#     issue_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.issues.issue_id",
#             name="fk_issue_message_ref_issues_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_repo_id_fk1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     msg_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.message.msg_id",
#             name="fk_issue_message_ref_message_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     issue_msg_ref_src_node_id = Column(
#         String(),
#         comment="This character based identifier comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API",
#     )
#     issue_msg_ref_src_comment_id = Column(
#         BigInteger,
#         comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue comments API",
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     message = relationship("Message", back_populates="issue")
#     issue = relationship("Issues", back_populates="msg_ref")

#     __tablename__ = "issue_message_ref"
#     __table_args__ = (
#         # insert on
#         UniqueConstraint(
#             "issue_msg_ref_src_comment_id", "tool_source", name="repo-issue"
#         ),
#         {"schema": "augur_data"},
#     )


# # TODO: Add relationship for cntrb_id
# # should repo_id be allowed to be NULL?


# class Issues(Base):
#     issue_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_issues_repo",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     reporter_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.contributors.cntrb_id", name="fk_issues_contributors_2"),
#         comment="The ID of the person who opened the issue. ",
#     )
#     pull_request = Column(BigInteger)
#     pull_request_id = Column(BigInteger)
#     created_at = Column(TIMESTAMP())
#     issue_title = Column(String())
#     issue_body = Column(String())
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.contributors.cntrb_id", name="fk_issues_contributors_1"),
#         comment="The ID of the person who closed the issue. ",
#     )
#     comment_count = Column(BigInteger)
#     updated_at = Column(TIMESTAMP())
#     closed_at = Column(TIMESTAMP())
#     due_on = Column(TIMESTAMP())
#     repository_url = Column(String())
#     issue_url = Column(String())
#     labels_url = Column(String())
#     comments_url = Column(String())
#     events_url = Column(String())
#     html_url = Column(String())
#     issue_state = Column(String())
#     issue_node_id = Column(String())
#     gh_issue_number = Column(BigInteger)
#     gh_issue_id = Column(BigInteger)
#     gh_user_id = Column(BigInteger)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     assignees = relationship("IssueAssignees")
#     events = relationship("IssueEvents")
#     labels = relationship("IssueLabels")

#     msg_ref = relationship("IssueMessageRef", back_populates="issue")

#     def get_messages(self):

#         messages = []
#         for msg_ref in self.msg_ref:
#             messages.append(msg_ref.message)

#         return messages

#     __tablename__ = "issues"
#     __table_args__ = (
#         Index("issue-cntrb-dix2", cntrb_id),
#         Index("issues_ibfk_1", repo_id),
#         Index("issues_ibfk_2", reporter_id),
#         Index("issues_ibfk_4", pull_request_id),
#         {"schema": "augur_data"},
#     )


# # TODO: Should latest_release_timestamp be a timestamp
# class Libraries(Base):
#     library_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_libraries_repo_1"),
#     )
#     platform = Column(String())
#     name = Column(String())
#     created_timestamp = Column(TIMESTAMP())
#     updated_timestamp = Column(TIMESTAMP())
#     library_description = Column(String())
#     keywords = Column(String())
#     library_homepage = Column(String())
#     license = Column(String())
#     version_count = Column(Integer)
#     latest_release_timestamp = Column(String())
#     latest_release_number = Column(String())
#     package_manager_id = Column(String())
#     dependency_count = Column(Integer)
#     dependent_library_count = Column(Integer)
#     primary_language = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     library_dependencies = relationship("LibraryDependecies")

#     # TODO: Should this be a one to one relationship with library version (this it what I defined it as)?
#     library_version = relationship("LibraryVersion", back_populates="library")

#     __tablename__ = "libraries"
#     __table_args__ = {"schema": "augur_data"}


# class LibraryDependecies(Base):
#     lib_dependency_id = Column(BigInteger, primary_key=True, nullable=False)
#     library_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.libraries.library_id",
#             name="fk_library_dependencies_libraries_1",
#         ),
#     )
#     manifest_platform = Column(String())
#     manifest_filepath = Column(String())
#     manifest_kind = Column(String())
#     repo_id_branch = Column(String(), nullable=False)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "library_dependencies"
#     __table_args__ = (Index("REPO_DEP", library_id), {"schema": "augur_data"})


# class LibraryVersion(Base):
#     library_version_id = Column(BigInteger, primary_key=True, nullable=False)
#     library_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.libraries.library_id", name="fk_library_version_libraries_1"
#         ),
#     )
#     library_platform = Column(String())
#     version_number = Column(String())
#     version_release_date = Column(TIMESTAMP())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     library = relationship("Libraries", back_populates="library_version")

#     __tablename__ = "library_version"
#     __table_args__ = {"schema": "augur_data"}


# class LstmAnomalyModels(Base):
#     model_id = Column(BigInteger, primary_key=True, nullable=False)
#     model_name = Column(String())
#     model_description = Column(String())
#     look_back_days = Column(BigInteger)
#     training_days = Column(BigInteger)
#     batch_size = Column(BigInteger)
#     metric = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     # TODO: Should this be a one to one relationship?
#     model_result = relationship("LstmAnomalyResults")

#     __tablename__ = "lstm_anomaly_models"
#     __table_args__ = {"schema": "augur_data"}


# class LstmAnomalyResults(Base):
#     result_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_lstm_anomaly_results_repo_1"),
#     )
#     repo_category = Column(String())
#     model_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.lstm_anomaly_models.model_id",
#             name="fk_lstm_anomaly_results_lstm_anomaly_models_1",
#         ),
#     )
#     metric = Column(String())
#     contamination_factor = Column(Float())
#     mean_absolute_error = Column(Float())
#     remarks = Column(String())
#     metric_field = Column(
#         String(),
#         comment="This is a listing of all of the endpoint fields included in the generation of the metric. Sometimes there is one, sometimes there is more than one. This will list them all. ",
#     )
#     mean_absolute_actual_value = Column(Float())
#     mean_absolute_prediction_value = Column(Float())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "lstm_anomaly_results"
#     __table_args__ = {"schema": "augur_data"}


# # TODO: I don't think that repo_id needs to be included because this behavior could be achieved by Repo.ParentObj.msg_ref.message (ParentObj is things such as prs or issues)
# # TODO: Add relationship to repo group list serve table


# class Message(Base):
#     msg_id = Column(BigInteger, primary_key=True, nullable=False)
#     rgls_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo_groups_list_serve.rgls_id",
#             name="fk_message_repo_groups_list_serve_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     platform_msg_id = Column(BigInteger)
#     platform_node_id = Column(String())
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_message_repoid",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_message_contributors_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#         comment="Not populated for mailing lists. Populated for GitHub issues. ",
#     )
#     msg_text = Column(String())
#     msg_timestamp = Column(TIMESTAMP())
#     msg_sender_email = Column(String())
#     msg_header = Column(String())
#     pltfrm_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.platform.pltfrm_id",
#             name="fk_message_platform_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#         nullable=False,
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     # Used this thread to determine how to do one to many relationship with an extra middle table: https://stackoverflow.com/questions/35795717/flask-sqlalchemy-many-to-many-relationship-with-extra-field
#     commit = relationship("CommitCommentRef", back_populates="message")
#     issue = relationship("IssueMessageRef", back_populates="message")
#     pull_request = relationship("PullRequestMessageRef", back_populates="message")
#     pr_review = relationship("PullRequestReviewMessageRef", back_populates="message")

#     analysis = relationship("MessageAnalysis", back_populates="message")
#     sentiment = relationship("MessageSentiment", back_populates="message")

#     __tablename__ = "message"
#     __table_args__ = (
#         UniqueConstraint("platform_msg_id", "tool_source", name="gh-message"),
#         Index("messagegrouper", msg_id, rgls_id, unique=True),
#         Index("msg-cntrb-id-idx", cntrb_id),
#         Index("platformgrouper", msg_id, pltfrm_id),
#         {"schema": "augur_data"},
#     )


# class MessageAnalysis(Base):
#     msg_analysis_id = Column(BigInteger, primary_key=True, nullable=False)
#     msg_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.message.msg_id", name="fk_message_analysis_message_1"),
#     )
#     worker_run_id = Column(
#         BigInteger,
#         comment="This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ",
#     )
#     sentiment_score = Column(
#         Float(),
#         comment="A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ",
#     )
#     reconstruction_error = Column(
#         Float(),
#         comment="Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.",
#     )
#     novelty_flag = Column(
#         Boolean(),
#         comment="This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ",
#     )
#     feeck_flag = Column(
#         Boolean(),
#         comment="This exists to provide the user with an opportunity provide feeck on the resulting the sentiment scores. ",
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     message = relationship("Message", back_populates="analysis")

#     __tablename__ = "message_analysis"
#     __table_args__ = {"schema": "augur_data"}


# class MessageAnalysisSummary(Base):
#     msg_summary_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id", name="fk_message_analysis_summary_repo_1"
#         ),
#     )
#     worker_run_id = Column(BigInteger)
#     positive_ratio = Column(Float())
#     negative_ratio = Column(Float())
#     novel_count = Column(BigInteger)
#     period = Column(TIMESTAMP())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     # TODO: Ensure that this is a one to one relationship
#     repo = relationship("Repo", back_populates="msg_analysis_summary")

#     __tablename__ = "message_analysis_summary"
#     __table_args__ = {"schema": "augur_data"}


# class MessageSentiment(Base):
#     msg_analysis_id = Column(BigInteger, primary_key=True, nullable=False)
#     msg_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.message.msg_id", name="fk_message_sentiment_message_1"),
#     )
#     worker_run_id = Column(
#         BigInteger,
#         comment="This column is used to indicate analyses run by a worker during the same execution period, and is useful for grouping, and time series analysis.  ",
#     )
#     sentiment_score = Column(
#         Float(),
#         comment="A sentiment analysis score. Zero is neutral, negative numbers are negative sentiment, and positive numbers are positive sentiment. ",
#     )
#     reconstruction_error = Column(
#         Float(),
#         comment="Each message is converted to a 250 dimensin doc2vec vector, so the reconstruction error is the difference between what the predicted vector and the actual vector.",
#     )
#     novelty_flag = Column(
#         Boolean(),
#         comment="This is an analysis of the degree to which the message is novel when compared to other messages in a repository.  For example when bots are producing numerous identical messages, the novelty score is low. It would also be a low novelty score when several people are making the same coment. ",
#     )
#     feedback = Column(
#         Boolean(),
#         comment="This exists to provide the user with an opportunity provide feedback on the resulting the sentiment scores. ",
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     message = relationship("Message", back_populates="sentiment")

#     __tablename__ = "message_sentiment"
#     __table_args__ = {"schema": "augur_data"}


# class MessageSentimentSummary(Base):
#     msg_summary_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id", name="fk_message_sentiment_summary_repo_1"
#         ),
#     )
#     worker_run_id = Column(
#         BigInteger,
#         comment='This value should reflect the worker_run_id for the messages summarized in the table. There is not a relation between these two tables for that purpose because its not *really*, relationaly a concept unless we create a third table for "worker_run_id", which we determined was unnecessarily complex. ',
#     )
#     positive_ratio = Column(Float())
#     negative_ratio = Column(Float())
#     novel_count = Column(
#         BigInteger,
#         comment="The number of messages identified as novel during the analyzed period",
#     )
#     period = Column(
#         TIMESTAMP(),
#         comment="The whole timeline is divided into periods based on the definition of time period for analysis, which is user specified. Timestamp of the first period to look at, until the end of messages at the data of execution. ",
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     repo = relationship("Repo", back_populates="msg_sentiment_summary")

#     __tablename__ = "message_sentiment_summary"
#     __table_args__ = {
#         "schema": "augur_data",
#         "comment": "In a relationally perfect world, we would have a table called “message_sentiment_run” the incremented the “worker_run_id” for both message_sentiment and message_sentiment_summary. For now, we decided this was overkill. ",
#     }


# class Platform(Base):
#     pltfrm_id = Column(BigInteger, nullable=False)
#     pltfrm_name = Column(String())
#     pltfrm_version = Column(String())
#     pltfrm_release_date = Column(Date)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     pr_reviews = relationship("PullRequestReviews")

#     __tablename__ = "platform"
#     __table_args__ = (
#         PrimaryKeyConstraint("pltfrm_id", name="theplat"),
#         Index("plat", pltfrm_id, unique=True),
#         {"schema": "augur_data"},
#     )


# class PullRequestAnalysis(Base):
#     pull_request_analysis_id = Column(BigInteger, primary_key=True, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_analysis_pull_requests_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#         comment="It would be better if the pull request worker is run first to fetch the latest PRs before analyzing",
#     )
#     merge_probability = Column(
#         Numeric(precision=256, scale=250),
#         comment="Indicates the probability of the PR being merged",
#     )
#     mechanism = Column(
#         String(),
#         comment="the ML model used for prediction (It is XGBoost Classifier at present)",
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )

#     pull_request = relationship("PullRequests", back_populates="analysis")

#     __tablename__ = "pull_request_analysis"
#     __table_args__ = (
#         Index("pr_anal_idx", pull_request_id),
#         Index("probability_idx", merge_probability.desc().nullslast()),
#         {"schema": "augur_data"},
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.assignees
# # TODO: Add relationship for cntrb_id


# class PullRequestAssignees(Base):
#     pr_assignee_map_id = Column(BigInteger, primary_key=True, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_assignees_pull_requests_1",
#         ),
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_pull_request_assignees_repo_id",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     contrib_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_pull_request_assignees_contributors_1",
#         ),
#     )
#     pr_assignee_src_id = Column(BigInteger)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "pull_request_assignees"
#     __table_args__ = (
#         Index("pr_meta_cntrb-idx", contrib_id),
#         {"schema": "augur_data"},
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.commits
# # TODO: Add relationship for cntrb_id
# class PullRequestCommits(Base):
#     pr_cmt_id = Column(BigInteger, primary_key=True, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_commits_pull_requests_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_pull_request_commits_repo_id",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#     )
#     pr_cmt_sha = Column(
#         String(),
#         comment="This is the commit SHA for a pull request commit. If the PR is not to the master branch of the main repository (or, in rare cases, from it), then you will NOT find a corresponding commit SHA in the commit table. (see table comment for further explanation). ",
#     )
#     pr_cmt_node_id = Column(String())
#     pr_cmt_message = Column(String())
#     pr_cmt_comments_url = Column(String())
#     pr_cmt_author_cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_pr_commit_cntrb_id",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     pr_cmt_timestamp = Column(TIMESTAMP())
#     pr_cmt_author_email = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "pull_request_commits"
#     __table_args__ = (
#         UniqueConstraint(
#             "pull_request_id", "repo_id", "pr_cmt_sha", name="pr_commit_nk"
#         ),
#         {
#             "schema": "augur_data",
#             "comment": "Pull request commits are an enumeration of each commit associated with a pull request. \nNot all pull requests are from a branch or fork into master. \nThe commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).\nTherefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. \nIn cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ",
#         },
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.events
# # TODO: Add relationship for cntrb_id


# class PullRequestEvents(Base):
#     pr_event_id = Column(BigInteger, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_events_pull_requests_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#         nullable=False,
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fkprevent_repo_id",
#             ondelete="RESTRICT",
#             onupdate="RESTRICT",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_pull_request_events_contributors_1",
#         ),
#         nullable=False,
#     )
#     action = Column(String(), nullable=False)
#     action_commit_hash = Column(String())
#     created_at = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )
#     issue_event_src_id = Column(
#         BigInteger,
#         comment="This ID comes from the source. In the case of GitHub, it is the id that is the first field returned from the issue events API",
#     )
#     node_id = Column(
#         String(),
#         comment="This should be renamed to issue_event_src_node_id, as its the varchar identifier in GitHub and likely common in other sources as well. However, since it was created before we came to this naming standard and workers are built around it, we have it simply named as node_id. Anywhere you see node_id in the schema, it comes from GitHubs terminology.",
#     )
#     node_url = Column(String())
#     platform_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.platform.pltfrm_id",
#             name="fkpr_platform",
#             ondelete="RESTRICT",
#             onupdate="RESTRICT",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#         server_default=text("25150"),
#     )
#     pr_platform_event_id = Column(BigInteger)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "pull_request_events"
#     __table_args__ = (
#         PrimaryKeyConstraint("pr_event_id", name="pr_events_pkey"),
#         UniqueConstraint(
#             "pr_platform_event_id", "platform_id", name="unique-pr-event-id"
#         ),
#         Index("pr_events_ibfk_1", pull_request_id),
#         Index("pr_events_ibfk_2", cntrb_id),
#         {"schema": "augur_data"},
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.files
# class PullRequestFiles(Base):
#     pr_file_id = Column(BigInteger, primary_key=True, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_commits_pull_requests_1_copy_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_pull_request_files_repo_id",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     pr_file_additions = Column(BigInteger)
#     pr_file_deletions = Column(BigInteger)
#     pr_file_path = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "pull_request_files"
#     __table_args__ = (
#         # TODO: Confirm: Values to determine if insert needed
#         UniqueConstraint(
#             "pull_request_id", "repo_id", "pr_file_path", name="prfiles_unique"
#         ),
#         {
#             "schema": "augur_data",
#             "comment": "Pull request commits are an enumeration of each commit associated with a pull request. \nNot all pull requests are from a branch or fork into master. \nThe commits table intends to count only commits that end up in the master branch (i.e., part of the deployed code base for a project).\nTherefore, there will be commit “SHA”’s in this table that are no associated with a commit SHA in the commits table. \nIn cases where the PR is to the master branch of a project, you will find a match. In cases where the PR does not involve the master branch, you will not find a corresponding commit SHA in the commits table. This is expected. ",
#         },
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.labels


# class PullRequestLabels(Base):
#     pr_label_id = Column(BigInteger, primary_key=True, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_labels_pull_requests_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_pull_request_labels_repo",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#     )
#     pr_src_id = Column(BigInteger)
#     pr_src_node_id = Column(String())
#     pr_src_url = Column(String())
#     pr_src_description = Column(String())
#     pr_src_color = Column(String())
#     pr_src_default_bool = Column(Boolean())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "pull_request_labels"
#     __table_args__ = (
#         # TODO: Confirm: Values to determine if insert needed
#         UniqueConstraint("pr_src_id", "pull_request_id", name="unique-pr-src-label-id"),
#         {"schema": "augur_data"},
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.msg_ref


# class PullRequestMessageRef(Base):
#     pr_msg_ref_id = Column(BigInteger, primary_key=True, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_message_ref_pull_requests_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_pr_repo",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#     )
#     msg_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.message.msg_id",
#             name="fk_pull_request_message_ref_message_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     pr_message_ref_src_comment_id = Column(BigInteger)
#     pr_message_ref_src_node_id = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())
#     pr_issue_url = Column(String())

#     message = relationship("Message", back_populates="pull_request")
#     pull_request = relationship("PullRequests", back_populates="msg_ref")

#     __tablename__ = "pull_request_message_ref"
#     __table_args__ = (
#         # TODO: Confirm: Values to determine if insert needed
#         UniqueConstraint(
#             "pr_message_ref_src_comment_id", "tool_source", name="pr-comment-nk"
#         ),
#         {"schema": "augur_data"},
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.meta_data


# class PullRequestMeta(Base):
#     pr_repo_meta_id = Column(BigInteger, primary_key=True, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_meta_pull_requests_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_pull_request_repo_meta_repo_id",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     pr_head_or_base = Column(
#         String(),
#         comment="Each pull request should have one and only one head record; and one and only one base record. ",
#     )
#     pr_src_meta_label = Column(String())
#     pr_src_meta_ref = Column(String())
#     pr_sha = Column(String())
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_pull_request_meta_contributors_2",
#         ),
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "pull_request_meta"
#     __table_args__ = (
#         Index("pr_meta-cntrbid-idx", cntrb_id),
#         {
#             "schema": "augur_data",
#             "comment": 'Pull requests contain referencing metadata.  There are a few columns that are discrete. There are also head and base designations for the repo on each side of the pull request. Similar functions exist in GitLab, though the language here is based on GitHub. The JSON Being adapted to as of the development of this schema is here:      "base": {       "label": "chaoss:dev",       "ref": "dev",       "sha": "dc6c6f3947f7dc84ecba3d8bda641ef786e7027d",       "user": {         "login": "chaoss",         "id": 29740296,         "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",         "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",         "gravatar_id": "",         "url": "https://api.github.com/users/chaoss",         "html_url": "https://github.com/chaoss",         "followers_url": "https://api.github.com/users/chaoss/followers",         "following_url": "https://api.github.com/users/chaoss/following{/other_user}",         "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",         "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",         "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",         "organizations_url": "https://api.github.com/users/chaoss/orgs",         "repos_url": "https://api.github.com/users/chaoss/repos",         "events_url": "https://api.github.com/users/chaoss/events{/privacy}",         "received_events_url": "https://api.github.com/users/chaoss/received_events",         "type": "Organization",         "site_admin": false       },       "repo": {         "id": 78134122,         "node_id": "MDEwOlJlcG9zaXRvcnk3ODEzNDEyMg==",         "name": "augur",         "full_name": "chaoss/augur",         "private": false,         "owner": {           "login": "chaoss",           "id": 29740296,           "node_id": "MDEyOk9yZ2FuaXphdGlvbjI5NzQwMjk2",           "avatar_url": "https://avatars2.githubusercontent.com/u/29740296?v=4",           "gravatar_id": "",           "url": "https://api.github.com/users/chaoss",           "html_url": "https://github.com/chaoss",           "followers_url": "https://api.github.com/users/chaoss/followers",           "following_url": "https://api.github.com/users/chaoss/following{/other_user}",           "gists_url": "https://api.github.com/users/chaoss/gists{/gist_id}",           "starred_url": "https://api.github.com/users/chaoss/starred{/owner}{/repo}",           "subscriptions_url": "https://api.github.com/users/chaoss/subscriptions",           "organizations_url": "https://api.github.com/users/chaoss/orgs",           "repos_url": "https://api.github.com/users/chaoss/repos",           "events_url": "https://api.github.com/users/chaoss/events{/privacy}",           "received_events_url": "https://api.github.com/users/chaoss/received_events",           "type": "Organization",           "site_admin": false         }, ',
#         },
#     )


# # TODO: Don't know enough about table structure to create relationship


# class PullRequestRepo(Base):
#     pr_repo_id = Column(BigInteger, primary_key=True, nullable=False)
#     pr_repo_meta_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_request_meta.pr_repo_meta_id",
#             name="fk_pull_request_repo_pull_request_meta_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     pr_repo_head_or_base = Column(
#         String(),
#         comment="For ease of validation checking, we should determine if the repository referenced is the head or base of the pull request. Each pull request should have one and only one of these, which is not enforcable easily in the database.",
#     )
#     pr_src_repo_id = Column(BigInteger)
#     pr_src_node_id = Column(String())
#     pr_repo_name = Column(String())
#     pr_repo_full_name = Column(String())
#     pr_repo_private_bool = Column(Boolean())
#     pr_cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_pull_request_repo_contributors_1",
#         ),
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "pull_request_repo"
#     __table_args__ = (
#         Index("pr-cntrb-idx-repo", pr_cntrb_id),
#         {
#             "schema": "augur_data",
#             "comment": "This table is for storing information about forks that exist as part of a pull request. Generally we do not want to track these like ordinary repositories. ",
#         },
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.reviews.msg_ref


# class PullRequestReviewMessageRef(Base):
#     pr_review_msg_ref_id = Column(BigInteger, nullable=False)
#     pr_review_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_request_reviews.pr_review_id",
#             name="fk_pull_request_review_message_ref_pull_request_reviews_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#         nullable=False,
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_review_repo",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#     )
#     msg_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.message.msg_id",
#             name="fk_pull_request_review_message_ref_message_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#         nullable=False,
#     )
#     pr_review_msg_url = Column(String())
#     pr_review_src_id = Column(BigInteger)
#     pr_review_msg_src_id = Column(BigInteger)
#     pr_review_msg_node_id = Column(String())
#     pr_review_msg_diff_hunk = Column(String())
#     pr_review_msg_path = Column(String())
#     pr_review_msg_position = Column(BigInteger)
#     pr_review_msg_original_position = Column(BigInteger)
#     pr_review_msg_commit_id = Column(String())
#     pr_review_msg_original_commit_id = Column(String())
#     pr_review_msg_updated_at = Column(TIMESTAMP())
#     pr_review_msg_html_url = Column(String())
#     pr_url = Column(String())
#     pr_review_msg_author_association = Column(String())
#     pr_review_msg_start_line = Column(BigInteger)
#     pr_review_msg_original_start_line = Column(BigInteger)
#     pr_review_msg_start_side = Column(String())
#     pr_review_msg_line = Column(BigInteger)
#     pr_review_msg_original_line = Column(BigInteger)
#     pr_review_msg_side = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     message = relationship("Message", back_populates="pr_review")
#     pr_review = relationship("PullRequestReviews", back_populates="msg_ref")

#     __tablename__ = "pull_request_review_message_ref"
#     __table_args__ = (
#         PrimaryKeyConstraint("pr_review_msg_ref_id", name="pr_review_msg_ref_id"),
#         UniqueConstraint("pr_review_msg_src_id", "tool_source", name="pr-review-nk"),
#         {"schema": "augur_data"},
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.reviewers
# # TODO: Add cntrb_id relationship (don't understand table well enough)


# class PullRequestReviewers(Base):
#     pr_reviewer_map_id = Column(BigInteger, primary_key=True, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_reviewers_pull_requests_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     pr_source_id = Column(
#         BigInteger,
#         comment="The platform ID for the pull/merge request. Used as part of the natural key, along with pr_reviewer_src_id in this table. ",
#     )
#     repo_id = Column(BigInteger)
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_pull_request_reviewers_contributors_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     pr_reviewer_src_id = Column(
#         BigInteger,
#         comment="The platform ID for the pull/merge request reviewer. Used as part of the natural key, along with pr_source_id in this table. ",
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "pull_request_reviewers"
#     __table_args__ = (
#         UniqueConstraint(
#             "pr_source_id",
#             "pr_reviewer_src_id",
#             name="unique_pr_src_reviewer_key",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#         Index("pr-reviewers-cntrb-idx1", cntrb_id),
#         {"schema": "augur_data"},
#     )


# # TODO: I don't think repo_id is needed on this table because it can be achieved by doing Repo.PullRequests.reviews
# # TODO: Add relationship for cntrb_id


# class PullRequestReviews(Base):
#     pr_review_id = Column(BigInteger, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_reviews_pull_requests_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#         nullable=False,
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_repo_review",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#     )
#     cntrb_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_pull_request_reviews_contributors_1",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#         nullable=False,
#     )
#     pr_review_author_association = Column(String())
#     pr_review_state = Column(String())
#     pr_review_body = Column(String())
#     pr_review_submitted_at = Column(TIMESTAMP())
#     pr_review_src_id = Column(BigInteger)
#     pr_review_node_id = Column(String())
#     pr_review_html_url = Column(String())
#     pr_review_pull_request_url = Column(String())
#     pr_review_commit_id = Column(String())
#     platform_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.platform.pltfrm_id",
#             name="fk-review-platform",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#             initially="DEFERRED",
#             deferrable=True,
#         ),
#         server_default=text("25150"),
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     msg_ref = relationship("PullRequestReviewMessageRef", back_populates="pr_review")

#     def get_messages(self):

#         messages = []
#         for msg_ref in self.msg_ref:
#             messages.append(msg_ref.message)

#         return messages

#     __tablename__ = "pull_request_reviews"
#     __table_args__ = (
#         PrimaryKeyConstraint("pr_review_id", name="pull_request_review_id"),
#         UniqueConstraint("pr_review_src_id", "tool_source", name="sourcepr-review-id"),
#         {"schema": "augur_data"},
#     )


# class PullRequestTeams(Base):
#     pr_team_id = Column(BigInteger, primary_key=True, nullable=False)
#     pull_request_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.pull_requests.pull_request_id",
#             name="fk_pull_request_teams_pull_requests_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     pr_src_team_id = Column(BigInteger)
#     pr_src_team_node = Column(String())
#     pr_src_team_url = Column(String())
#     pr_team_name = Column(String())
#     pr_team_slug = Column(String())
#     pr_team_description = Column(String())
#     pr_team_privacy = Column(String())
#     pr_team_permission = Column(String())
#     pr_team_src_members_url = Column(String())
#     pr_team_src_repositories_url = Column(String())
#     pr_team_parent_id = Column(BigInteger)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "pull_request_teams"
#     __table_args__ = {"schema": "augur_data"}


# class PullRequests(Base):
#     pull_request_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="fk_pull_requests_repo_1",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#         server_default=text("0"),
#     )
#     pr_url = Column(String())
#     pr_src_id = Column(
#         BigInteger, comment="The pr_src_id is unique across all of github."
#     )
#     pr_src_node_id = Column(String())
#     pr_html_url = Column(String())
#     pr_diff_url = Column(String())
#     pr_patch_url = Column(String())
#     pr_issue_url = Column(String())
#     pr_augur_issue_id = Column(
#         BigInteger, comment="This is to link to the augur stored related issue"
#     )
#     pr_src_number = Column(
#         BigInteger, comment="The pr_src_number is unique within a repository."
#     )
#     pr_src_state = Column(String())
#     pr_src_locked = Column(Boolean())
#     pr_src_title = Column(String())
#     pr_augur_contributor_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.contributors.cntrb_id",
#             name="fk_pr_contribs",
#             ondelete="RESTRICT",
#             onupdate="CASCADE",
#         ),
#         comment="This is to link to the augur contributor record. ",
#     )
#     pr_body = Column(Text())
#     pr_created_at = Column(TIMESTAMP())
#     pr_updated_at = Column(TIMESTAMP())
#     pr_closed_at = Column(TIMESTAMP())
#     pr_merged_at = Column(TIMESTAMP())
#     pr_merge_commit_sha = Column(String())
#     pr_teams = Column(BigInteger, comment="One to many with pull request teams. ")
#     pr_milestone = Column(String())
#     pr_commits_url = Column(String())
#     pr_review_comments_url = Column(String())
#     pr_review_comment_url = Column(
#         String(),
#         comment="This is a field with limited utility. It does expose how to access a specific comment if needed with parameters. If the source changes URL structure, it may be useful",
#     )
#     pr_comments_url = Column(String())
#     pr_statuses_url = Column(String())
#     pr_meta_head_id = Column(
#         String(),
#         comment="The metadata for the head repo that links to the pull_request_meta table. ",
#     )
#     pr_meta_base_id = Column(
#         String(),
#         comment="The metadata for the base repo that links to the pull_request_meta table. ",
#     )
#     pr_src_issue_url = Column(String())
#     pr_src_comments_url = Column(String())
#     pr_src_review_comments_url = Column(String())
#     pr_src_commits_url = Column(String())
#     pr_src_statuses_url = Column(String())
#     pr_src_author_association = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     analysis = relationship("PullRequestAnalysis", back_populates="pull_request")
#     assignees = relationship("PullRequestAssignees")
#     commits = relationship("PullRequestCommits")
#     events = relationship("PullRequestEvents")
#     files = relationship("PullRequestFiles")
#     labels = relationship("PullRequestLabels")
#     msg_ref = relationship("PullRequestMessageRef", back_populates="pull_request")
#     meta_data = relationship("PullRequestMeta")
#     reviewers = relationship("PullRequestReviewers")
#     reviews = relationship("PullRequestReviews")
#     teams = relationship("PullRequestTeams")

#     def get_messages(self):

#         messages = []
#         for msg_ref in self.msg_ref:
#             messages.append(msg_ref.message)

#         return messages

#     __tablename__ = "pull_requests"
#     __table_args__ = (
#         Index(
#             "id_node", pr_src_id.desc().nullsfirst(), pr_src_node_id.desc().nullsfirst()
#         ),
#         Index("pull_requests_idx_repo_id_data_datex", repo_id, data_collection_date),
#         {"schema": "augur_data"},
#     )


# class Releases(Base):
#     release_id = Column(CHAR(length=64), primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_releases_repo_1"),
#         nullable=False,
#     )
#     release_name = Column(String())
#     release_description = Column(String())
#     release_author = Column(String())
#     release_created_at = Column(TIMESTAMP())
#     release_published_at = Column(TIMESTAMP())
#     release_updated_at = Column(TIMESTAMP())
#     release_is_draft = Column(Boolean())
#     release_is_prerelease = Column(Boolean())
#     release_tag_name = Column(String())
#     release_url = Column(String())
#     tag_only = Column(Boolean())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "releases"
#     __table_args__ = {"schema": "augur_data"}


# class Repo(Base):
#     repo_id = Column(BigInteger, nullable=False)
#     repo_group_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo_groups.repo_group_id", name="fk_repo_repo_groups_1"
#         ),
#         nullable=False,
#     )
#     repo_git = Column(String(), nullable=False)
#     repo_path = Column(String(), server_default="NULL")
#     repo_name = Column(String(), server_default="NULL")
#     repo_added = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )
#     repo_status = Column(String(), nullable=False, server_default="New")
#     repo_type = Column(
#         String(),
#         server_default="",
#         comment='This field is intended to indicate if the repository is the "main instance" of a repository in cases where implementations choose to add the same repository to more than one repository group. In cases where the repository group is of rg_type Github Organization then this repo_type should be "primary". In other cases the repo_type should probably be "user created". We made this a varchar in order to hold open the possibility that there are additional repo_types we have not thought about. ',
#     )
#     url = Column(String())
#     owner_id = Column(Integer)
#     description = Column(String())
#     primary_language = Column(String())
#     created_at = Column(String())
#     forked_from = Column(String())
#     updated_at = Column(TIMESTAMP())
#     repo_archived_date_collected = Column(TIMESTAMP(timezone=True))
#     repo_archived = Column(Integer)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     commits = relationship("Commits")
#     issues = relationship("Issues")
#     pull_requests = relationship("PullRequests")
#     libraries = relationship("Libraries")
#     messages = relationship("Message")

#     pr_assignees = relationship("PullRequestAssignees")
#     pr_commits = relationship("PullRequestCommits")
#     pr_events = relationship("PullRequestEvents")
#     pr_files = relationship("PullRequestFiles")
#     pr_labels = relationship("PullRequestLabels")
#     pr_meta_data = relationship("PullRequestMeta")
#     pr_reviews = relationship("PullRequestReviews")

#     msg_analysis_summary = relationship("MessageAnalysisSummary", back_populates="repo")
#     msg_sentiment_summary = relationship(
#         "MessageSentimentSummary", back_populates="repo"
#     )

#     lstm_anomaly_results = relationship("LstmAnomalyResults")

#     releases = relationship("Releases")
#     badges = relationship("RepoBadging")
#     cluster_messages = relationship("RepoClusterMessages")
#     dependencies = relationship("RepoDependencies")
#     deps_libyear = relationship("RepoDepsLibyear")
#     deps_scorecard_id = relationship("RepoDepsScorecard")

#     info = relationship("RepoInfo")
#     insights = relationship("RepoInsights")
#     insight_records = relationship("RepoInsightsRecords")

#     labor = relationship("RepoLabor")
#     meta_data = relationship("RepoMeta")
#     sbom_scans = relationship("RepoSbomScans")
#     stats = relationship("RepoStats")
#     topic = relationship("RepoTopic")

#     __tablename__ = "repo"
#     __table_args__ = (
#         PrimaryKeyConstraint("repo_id", name="repounique"),
#         Index("forked", forked_from),
#         Index("repo_idx_repo_id_repo_namex", repo_id, repo_name),
#         Index("repogitindexrep", repo_git),
#         Index("reponameindex", repo_name, postgresql_using="hash"),
#         Index("reponameindexbtree", repo_name),
#         Index("rggrouponrepoindex", repo_group_id),
#         Index("therepo", repo_id, unique=True),
#         {
#             "schema": "augur_data",
#             "comment": "This table is a combination of the columns in Facade’s repo table and GHTorrent’s projects table. ",
#         },
#     )


# class RepoBadging(Base):
#     badge_collection_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_repo_badging_repo_1"),
#     )
#     created_at = Column(TIMESTAMP(), server_default=func.current_timestamp())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())
#     data = Column(JSONB())

#     __tablename__ = "repo_badging"
#     __table_args__ = {
#         "schema": "augur_data",
#         "comment": "This will be collected from the LF’s Badging API\nhttps://bestpractices.coreinfrastructure.org/projects.json?pq=https%3A%2F%2Fgithub.com%2Fchaoss%2Faugur\n",
#     }


# class RepoClusterMessages(Base):
#     msg_cluster_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_repo_cluster_messages_repo_1"),
#     )
#     cluster_content = Column(Integer)
#     cluster_mechanism = Column(Integer)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_cluster_messages"
#     __table_args__ = {"schema": "augur_data"}


# class RepoDependencies(Base):
#     repo_dependencies_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="repo_id"),
#         comment="Forign key for repo id. ",
#     )
#     dep_name = Column(String(), comment="Name of the dependancy found in project. ")
#     dep_count = Column(Integer, comment="Number of times the dependancy was found. ")
#     dep_language = Column(String(), comment="Language of the dependancy. ")
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_dependencies"
#     __table_args__ = {
#         "schema": "augur_data",
#         "comment": "Contains the dependencies for a repo.",
#     }


# # TODO: typo in field current_verion
# class RepoDepsLibyear(Base):
#     repo_deps_libyear_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger, ForeignKey("augur_data.repo.repo_id", name="repo_id_copy_2")
#     )
#     name = Column(String())
#     requirement = Column(String())
#     type = Column(String())
#     package_manager = Column(String())
#     current_verion = Column(String())
#     latest_version = Column(String())
#     current_release_date = Column(String())
#     latest_release_date = Column(String())
#     libyear = Column(Float())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_deps_libyear"
#     __table_args__ = {"schema": "augur_data"}


# class RepoDepsScorecard(Base):
#     repo_deps_scorecard_id = Column(BigInteger, nullable=False)
#     repo_id = Column(
#         BigInteger, ForeignKey("augur_data.repo.repo_id", name="repo_id_copy_1")
#     )
#     name = Column(String())
#     status = Column(String())
#     score = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_deps_scorecard"
#     __table_args__ = (
#         PrimaryKeyConstraint(
#             "repo_deps_scorecard_id", name="repo_deps_scorecard_pkey1"
#         ),
#         {"schema": "augur_data"},
#     )


# class RepoGroupInsights(Base):
#     rgi_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_group_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo_groups.repo_group_id",
#             name="fk_repo_group_insights_repo_groups_1",
#         ),
#     )
#     rgi_metric = Column(String())
#     rgi_value = Column(String())
#     cms_id = Column(BigInteger)
#     rgi_fresh = Column(
#         Boolean(),
#         comment='false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ',
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     repo_group = relationship("RepoGroups")

#     __tablename__ = "repo_group_insights"
#     __table_args__ = {
#         "schema": "augur_data",
#         "comment": 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a REPOSITORY_GROUP and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. \n\nWorker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ',
#     }


# class RepoGroups(Base):
#     repo_group_id = Column(BigInteger, nullable=False)
#     rg_name = Column(String(), nullable=False)
#     rg_description = Column(String(), server_default="NULL")
#     rg_website = Column(String(), server_default="NULL")
#     rg_recache = Column(SmallInteger, server_default=text("1"))
#     rg_last_modified = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )
#     rg_type = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     repos = relationship("Repo")
#     rg_list_serve = relationship("RepoGroupsListServe")

#     __tablename__ = "repo_groups"
#     __table_args__ = (
#         PrimaryKeyConstraint("repo_group_id", name="rgid"),
#         Index("rgidm", repo_group_id, unique=True),
#         Index("rgnameindex", rg_name),
#         {
#             "schema": "augur_data",
#             "comment": "rg_type is intended to be either a GitHub Organization or a User Created Repo Group. ",
#         },
#     )


# class RepoGroupsListServe(Base):
#     rgls_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_group_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo_groups.repo_group_id",
#             name="fk_repo_groups_list_serve_repo_groups_1",
#         ),
#         nullable=False,
#     )
#     rgls_name = Column(String())
#     rgls_description = Column(String())
#     rgls_sponsor = Column(String())
#     rgls_email = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_groups_list_serve"
#     __table_args__ = (
#         UniqueConstraint("rgls_id", "repo_group_id", name="rglistserve"),
#         Index("lister", rgls_id, repo_group_id, unique=True),
#         {"schema": "augur_data"},
#     )


# class RepoInfo(Base):
#     repo_info_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_repo_info_repo_1"),
#         nullable=False,
#     )
#     last_updated = Column(TIMESTAMP())
#     issues_enabled = Column(String())
#     open_issues = Column(Integer)
#     pull_requests_enabled = Column(String())
#     wiki_enabled = Column(String())
#     pages_enabled = Column(String())
#     fork_count = Column(Integer)
#     default_branch = Column(String())
#     watchers_count = Column(Integer)
#     UUID = Column(Integer)
#     license = Column(String())
#     stars_count = Column(Integer)
#     committers_count = Column(Integer)
#     issue_contributors_count = Column(String())
#     changelog_file = Column(String())
#     contributing_file = Column(String())
#     license_file = Column(String())
#     code_of_conduct_file = Column(String())
#     security_issue_file = Column(String())
#     security_audit_file = Column(String())
#     status = Column(String())
#     keywords = Column(String())
#     commit_count = Column(BigInteger)
#     issues_count = Column(BigInteger)
#     issues_closed = Column(BigInteger)
#     pull_request_count = Column(BigInteger)
#     pull_requests_open = Column(BigInteger)
#     pull_requests_closed = Column(BigInteger)
#     pull_requests_merged = Column(BigInteger)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_info"
#     __table_args__ = (
#         # TODO: Their appears to be two of the same index in current database
#         Index("repo_info_idx_repo_id_data_date_1x", repo_id, data_collection_date),
#         {"schema": "augur_data"},
#     )


# # TODO: Why is numeric defined without level or precision?
# class RepoInsights(Base):
#     ri_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_repo_insights_repo_1"),
#     )
#     ri_metric = Column(String())
#     ri_value = Column(String())
#     ri_date = Column(TIMESTAMP())
#     ri_fresh = Column(
#         Boolean(),
#         comment='false if the date is before the statistic that triggered the insight, true if after. This allows us to automatically display only "fresh insights" and avoid displaying "stale insights". The insight worker will populate this table. ',
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())
#     ri_score = Column(Numeric())
#     ri_field = Column(String())
#     ri_detection_method = Column(String())

#     __tablename__ = "repo_insights"
#     __table_args__ = {
#         "schema": "augur_data",
#         "comment": 'This table is output from an analytical worker inside of Augur. It runs through the different metrics on a repository and identifies the five to ten most “interesting” metrics as defined by some kind of delta or other factor. The algorithm is going to evolve. \n\nWorker Design Notes: The idea is that the "insight worker" will scan through a bunch of active metrics or "synthetic metrics" to list the most important insights. ',
#     }


# class RepoInsightsRecords(Base):
#     ri_id = Column(
#         BigInteger, primary_key=True, nullable=False, comment="Primary key. "
#     )
#     repo_id = Column(
#         BigInteger,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="repo_id_ref",
#             ondelete="SET NULL",
#             onupdate="CASCADE",
#         ),
#         comment="Refers to repo table primary key. Will have a foreign key",
#     )
#     ri_metric = Column(String(), comment="The metric endpoint")
#     ri_field = Column(String(), comment="The field in the metric endpoint")
#     ri_value = Column(String(), comment="The value of the endpoint in ri_field")
#     ri_date = Column(
#         TIMESTAMP(),
#         comment="The date the insight is for; in other words, some anomaly occurred on this date. ",
#     )
#     ri_score = Column(Float(), comment="A Score, derived from the algorithm used. ")
#     ri_detection_method = Column(
#         String(),
#         comment='A confidence interval or other expression of the type of threshold and the value of a threshold met in order for it to be "an insight". Example. "95% confidence interval". ',
#     )
#     tool_source = Column(String(), comment="Standard Augur Metadata")
#     tool_version = Column(String(), comment="Standard Augur Metadata")
#     data_source = Column(String(), comment="Standard Augur Metadata")
#     data_collection_date = Column(
#         TIMESTAMP(),
#         server_default=func.current_timestamp(),
#         comment="Standard Augur Metadata",
#     )

#     __tablename__ = "repo_insights_records"
#     __table_args__ = (Index("dater", ri_date), {"schema": "augur_data"})


# class RepoLabor(Base):
#     repo_labor_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_repo_labor_repo_1"),
#     )
#     repo_clone_date = Column(TIMESTAMP())
#     rl_analysis_date = Column(TIMESTAMP())
#     programming_language = Column(String())
#     file_path = Column(String())
#     file_name = Column(String())
#     total_lines = Column(Integer)
#     code_lines = Column(Integer)
#     comment_lines = Column(Integer)
#     blank_lines = Column(Integer)
#     code_complexity = Column(Integer)
#     repo_url = Column(
#         String(),
#         comment="This is a convenience column to simplify analysis against external datasets",
#     )
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_labor"
#     __table_args__ = {
#         "schema": "augur_data",
#         "comment": "repo_labor is a derivative of tables used to store scc code and complexity counting statistics that are inputs to labor analysis, which are components of CHAOSS value metric calculations. ",
#     }


# class RepoMeta(Base):
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_repo_meta_repo_1"),
#         primary_key=True,
#         nullable=False,
#     )
#     rmeta_id = Column(BigInteger, primary_key=True, nullable=False)
#     rmeta_name = Column(String())
#     rmeta_value = Column(String(), server_default=text("0"))
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_meta"
#     __table_args__ = {"schema": "augur_data", "comment": "Project Languages"}


# class RepoSbomScans(Base):
#     rsb_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         Integer,
#         ForeignKey(
#             "augur_data.repo.repo_id",
#             name="repo_linker_sbom",
#             ondelete="CASCADE",
#             onupdate="CASCADE",
#         ),
#     )
#     sbom_scan = Column(JSON())

#     __tablename__ = "repo_sbom_scans"
#     __table_args__ = {"schema": "augur_data"}


# class RepoStats(Base):
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_repo_stats_repo_1"),
#         primary_key=True,
#         nullable=False,
#     )
#     rstat_id = Column(BigInteger, primary_key=True, nullable=False)
#     rstat_name = Column(String())
#     rstat_value = Column(BigInteger)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_stats"
#     __table_args__ = {"schema": "augur_data", "comment": "Project Watchers"}


# class RepoTestCoverage(Base):
#     repo_id = Column(
#         BigInteger,
#         ForeignKey("augur_data.repo.repo_id", name="fk_repo_test_coverage_repo_1"),
#         primary_key=True,
#         nullable=False,
#     )
#     repo_clone_date = Column(TIMESTAMP())
#     rtc_analysis_date = Column(TIMESTAMP())
#     programming_language = Column(String())
#     file_path = Column(String())
#     file_name = Column(String())
#     testing_tool = Column(String())
#     file_statement_count = Column(BigInteger)
#     file_subroutine_count = Column(BigInteger)
#     file_statements_tested = Column(BigInteger)
#     file_subroutines_tested = Column(BigInteger)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_test_coverage"
#     __table_args__ = {"schema": "augur_data"}


# class RepoTopic(Base):
#     repo_topic_id = Column(BigInteger, primary_key=True, nullable=False)
#     repo_id = Column(
#         Integer,
#         ForeignKey("augur_data.repo.repo_id", name="fk_repo_topic_repo_1"),
#     )
#     topic_id = Column(Integer)
#     topic_prob = Column(Float())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "repo_topic"
#     __table_args__ = {"schema": "augur_data"}


# # TODO: Add foreign key to repo table


# class ReposFetchLog(Base):
#     repos_fetch_log_id = Column(BigInteger, primary_key=True)
#     repos_id = Column(Integer, nullable=False)
#     status = Column(String(), nullable=False)
#     date = Column(TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

#     __tablename__ = "repos_fetch_log"
#     __table_args__ = (
#         # TODO: There appear to be two identical indexes
#         Index("repos_id,status", repos_id, status),
#         {"schema": "augur_data"},
#     )


# class Settings(Base):
#     id = Column(Integer, primary_key=True, nullable=False)
#     setting = Column(String(), nullable=False)
#     value = Column(String(), nullable=False)
#     last_modified = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )

#     __tablename__ = "settings"
#     __table_args__ = {"schema": "augur_data"}


# class TopicWords(Base):
#     topic_words_id = Column(BigInteger, primary_key=True, nullable=False)
#     topic_id = Column(BigInteger)
#     word = Column(String())
#     word_prob = Column(Float())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "topic_words"
#     __table_args__ = {"schema": "augur_data"}


# # TODO: Add foreign key to repo_group table


# class UnknownCache(Base):
#     unknown_cache_id = Column(BigInteger, primary_key=True)
#     type = Column(String(), nullable=False)
#     repo_group_id = Column(Integer, nullable=False)
#     email = Column(String(), nullable=False)
#     domain = Column(String(), server_default="NULL")
#     added = Column(BigInteger, nullable=False)
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "unknown_cache"
#     __table_args__ = (
#         Index("type,projects_id", type, repo_group_id),
#         {"schema": "augur_data"},
#     )


# class UnresolvedCommitEmails(Base):
#     email_unresolved_id = Column(BigInteger, primary_key=True, nullable=False)
#     email = Column(String(), nullable=False)
#     name = Column(String())
#     tool_source = Column(String())
#     tool_version = Column(String())
#     data_source = Column(String())
#     data_collection_date = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "unresolved_commit_emails"
#     __table_args__ = (
#         UniqueConstraint("email", name="unresolved_commit_emails_email_key"),
#         {"schema": "augur_data"},
#     )


# class UtilityLog(Base):
#     id = Column(BigInteger, primary_key=True, nullable=False)
#     level = Column(String(), nullable=False)
#     status = Column(String(), nullable=False)
#     attempted = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )

#     __tablename__ = "utility_log"
#     __table_args__ = {"schema": "augur_data"}


# # TODO: Add foreign key to repo table


# class WorkingCommits(Base):
#     working_commits_id = Column(BigInteger, primary_key=True)
#     repos_id = Column(Integer, nullable=False)
#     working_commit = Column(String(), server_default="NULL")

#     __tablename__ = "working_commits"
#     __table_args__ = {"schema": "augur_data"}


# # class WorkingCommits(Base):
# #     working_commits_id = Column(BigInteger)
# #     repos_id = Column(Integer, nullable=False)
# #     working_commit = Column(String())

# #     __tablename__ = 'working_commits'
# #     __table_args__ = (
# #         PrimaryKeyConstraint('working_commits_id'),
# #         {"schema":"augur_operations"}
# #     )

# from augur.db.models.base import Base
# from sqlalchemy import (
#     Index,
#     Column,
#     Integer,
#     String,
#     UniqueConstraint,
#     BigInteger,
#     TIMESTAMP,
#     PrimaryKeyConstraint,
#     func,
#     text,
# )

# # Start of Augur Operations tablespoon
# class All(Base):
#     all_id = Column(BigInteger, primary_key=True)
#     Name = Column(String())
#     Bytes = Column(String())
#     Lines = Column(String())
#     Code = Column(String())
#     Comment = Column(String())
#     Blank = Column(String())
#     Complexity = Column(String())
#     Count = Column(String())
#     WeightedComplexity = Column(String())
#     Files = Column(String())

#     __tablename__ = "all"
#     __table_args__ = {"schema": "augur_operations"}


# class AugurSettings(Base):
#     id = Column(BigInteger)
#     setting = Column(String())
#     value = Column(String())
#     last_modified = Column(TIMESTAMP(), server_default=func.current_timestamp())

#     __tablename__ = "augur_settings"
#     __table_args__ = (
#         PrimaryKeyConstraint("id"),
#         UniqueConstraint("setting", name="setting-unique"),
#         {"schema": "augur_operations"},
#     )


# class ReposFetchLog(Base):
#     repos_fetch_log_id = Column(BigInteger)
#     repos_id = Column(Integer, nullable=False)
#     status = Column(String(), nullable=False)
#     date = Column(TIMESTAMP(), nullable=False, server_default=func.current_timestamp())

#     __tablename__ = "repos_fetch_log"
#     __table_args__ = (
#         PrimaryKeyConstraint("repos_fetch_log_id"),
#         Index("repos_id,statusops", repos_id, status),
#         {"schema": "augur_operations"},
#     )


# # TODO: Add foreign key to Repo table
# class WorkerHistory(Base):
#     history_id = Column(BigInteger)
#     repo_id = Column(BigInteger)
#     worker = Column(String(), nullable=False)
#     job_model = Column(String(), nullable=False)
#     oauth_id = Column(Integer)
#     timestamp = Column(TIMESTAMP(), nullable=False)
#     status = Column(String(), nullable=False)
#     total_results = Column(Integer)

#     __tablename__ = "worker_history"
#     __table_args__ = (
#         PrimaryKeyConstraint("history_id", name="history_pkey"),
#         {"schema": "augur_operations"},
#     )


# class WorkerJob(Base):
#     job_model = Column(String())
#     state = Column(Integer, nullable=False, server_default=text("0"))
#     zombie_head = Column(Integer)
#     since_id_str = Column(String(), nullable=False, server_default="0")
#     description = Column(String(), server_default="None")
#     last_count = Column(Integer)
#     last_run = Column(TIMESTAMP())
#     analysis_state = Column(Integer, server_default=text("0"))
#     oauth_id = Column(Integer, nullable=False)

#     __tablename__ = "worker_job"
#     __table_args__ = (
#         PrimaryKeyConstraint("job_model", name="job_pkey"),
#         {"schema": "augur_operations"},
#     )


# class WorkerOauth(Base):
#     oauth_id = Column(BigInteger)
#     name = Column(String(), nullable=False)
#     consumer_key = Column(String(), nullable=False)
#     consumer_secret = Column(String(), nullable=False)
#     access_token = Column(String(), nullable=False)
#     access_token_secret = Column(String(), nullable=False)
#     repo_directory = Column(String())
#     platform = Column(String(), server_default="github")

#     __tablename__ = "worker_oauth"
#     __table_args__ = (PrimaryKeyConstraint("oauth_id"), {"schema": "augur_operations"})


# class WorkerSettingsFacade(Base):
#     id = Column(Integer)
#     setting = Column(String(), nullable=False)
#     value = Column(String(), nullable=False)
#     last_modified = Column(
#         TIMESTAMP(), nullable=False, server_default=func.current_timestamp()
#     )

#     __tablename__ = "worker_settings_facade"
#     __table_args__ = (
#         PrimaryKeyConstraint("id", name="settings_pkey"),
#         {"schema": "augur_operations"},
#     )

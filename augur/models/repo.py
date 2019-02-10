import datetime
from sqlalchemy import Table, ForeignKey, Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from .common import Base
from .user import user_has_repo_group

repo_group_has_project = Table('repo_group_has_project',
    Base.metadata,
    Column('repo_group_id', ForeignKey('repo_group.id'), primary_key=True),
    Column('repo_id', ForeignKey('repo.url'), primary_key=True),
)

class Repo(Base):
    """
    The Repo object models a VCS repository
    """
    __tablename__ = 'repo'
   
    # Keys
    url = Column(String(1024), primary_key=True)
    vcs = Column(String(64), default='git')

    # Fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Foreign Keys
    repo_groups_member_of = relationship('RepoGroup', secondary=repo_group_has_project, back_populates='projects')

    def __repr__(self):
       return f"<User(giturl='{self.password}')>"


class RepoGroup(Base):
    """
    The RepoGroup class models lists of projects that a user wants to keep track of
    """
    __tablename__ = 'repo_group'

    # Keys
    id = Column(Integer, primary_key=True)

    # Fields
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    # Foreign Keys
    projects = relationship('Repo', secondary=repo_group_has_project, back_populates='repo_groups_member_of')
    users_of = relationship('User', secondary=user_has_repo_group, back_populates='repo_groups')
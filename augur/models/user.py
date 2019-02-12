import datetime
from sqlalchemy import Table, ForeignKey, Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from .common import Base
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

user_has_repo_group = Table('user_has_repo_group',
    Base.metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True),
    Column('repo_group_id', ForeignKey('repo_group.id'), primary_key=True),
)

class User(Base):
    """
    The User object models users in the database.
    """
    __tablename__ = 'user'

    # Keys
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(64), unique=True, nullable=False)

    # Fields
    password_hash = Column(String(128))
    email_confirmation_token = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    password_updated_at = Column(DateTime, default=datetime.datetime.utcnow)
    last_login_at = Column(DateTime, nullable=True)
    authenticated = Column(Boolean, default=False)
    active = Column(Boolean, default=True)
    
    # Foreign Keys
    repo_groups = relationship('RepoGroup', secondary=user_has_repo_group, back_populates='users_of')

    def get_id(self):
        return self.id

    def __repr__(self):
       return f"<User(username='{self.username}', email='{self.email}')>"

    @hybrid_property
    def password(self):
        return self.password_hash

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        # False as we do not support annonymity
        return self.active

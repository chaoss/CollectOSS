# coding: utf-8
from sqlalchemy import BigInteger, SmallInteger, Column, Index, Integer, String, Table, text, UniqueConstraint, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, UUID
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash
import logging 
import secrets

from augur.application.db.models.base import Base

logger = logging.getLogger(__name__)

def get_session():
    global session

    if "session" not in globals():
        from augur.application.db.session import DatabaseSession
        session = DatabaseSession(logger)

    return session
    
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

    groups = relationship("UserGroup")
    tokens = relationship("UserSessionToken")
    applications = relationship("ClientApplication")

    _is_authenticated = False
    _is_active = True
    _is_anoymous = True

    @property
    def is_authenticated(self):
        return self._is_authenticated

    @is_authenticated.setter
    def is_authenticated(self, val):
        self._is_authenticated = val

    @property
    def is_active(self):
        return self._is_active

    @is_active.setter
    def is_active(self, val):
        self._is_active = val

    @property
    def is_anoymous(self):
        return self._is_anoymous

    @is_anoymous.setter
    def is_anoymous(self, val):
        self._is_anoymous = val

    @staticmethod
    def exists(username):
        return User.get_user(username) is not None

    def get_id(self):
        return self.login_name

    def validate(self, password) -> bool:

        if not password:
            return False

        result = check_password_hash(self.login_hashword, password)
        return result

    @staticmethod
    def get_user(username: str):

        if not username:
            return None

        local_session = get_session()

        try:
            user = local_session.query(User).filter(User.login_name == username).one()
            return user
        except NoResultFound:
            return None
                
    @staticmethod
    def create_user(username: str, password: str, email: str, first_name:str, last_name:str, admin=False):

        if username is None or password is None or email is None or first_name is None or last_name is None:
            return False, {"status": "Missing field"} 

        local_session = get_session()

        user = local_session.query(User).filter(User.login_name == username).first()
        if user is not None:
            return False, {"status": "A User already exists with that username"}

        emailCheck = local_session.query(User).filter(User.email == email).first()
        if emailCheck is not None:
            return False, {"status": "A User already exists with that email"}

        try:
            user = User(login_name = username, login_hashword = generate_password_hash(password), email = email, first_name = first_name, last_name = last_name, tool_source="User API", tool_version=None, data_source="API", admin=admin)
            local_session.add(user)
            local_session.commit()

            result = user.add_group("default")
            if not result[0] and result[1]["status"] != "Group already exists":
                return False, {"status": "Failed to add default group for the user"}

            return True, {"status": "Account successfully created"}
        except AssertionError as exception_message: 
            return False, {"Error": f"{exception_message}."}

    def delete(self):

        local_session = get_session()

        for group in self.groups:
            user_repos_list = group.repos

            for user_repo_entry in user_repos_list:
                local_session.delete(user_repo_entry)

            local_session.delete(group)

        local_session.delete(self)
        local_session.commit()

        return True, {"status": "User deleted"}

    def update_password(self, old_password, new_password):

        local_session = get_session()

        if not old_password or not new_password:
            print("Need old and new password to update the password")
            return False,  {"status": "Need old and new password to update the password"}

        if not check_password_hash(self.login_hashword, old_password):
            print("Password did not match the users password, unable to update password")
            return False, {"status": "Password did not match users password"}

        self.login_hashword = generate_password_hash(new_password)
        local_session.commit()
        # print("Password Updated")

        return True, {"status": "Password updated"}

    def update_email(self, new_email):

        local_session = get_session()

        if not new_email:
            print("Need new email to update the email")
            return False, {"status": "Missing argument"}

        existing_user = local_session.query(User).filter(User.email == new_email).first()
        if existing_user is not None:
            print("Func: update_user. Error: Already an account with this email")
            return False, {"status": "There is already an account with this email"}

        self.email = new_email
        local_session.commit()
        # print("Email Updated")
        return True, {"status": "Email updated"}

    def update_username(self, new_username):

        local_session = get_session()

        if not new_username:
            print("Need new username to update the username")
            return False, {"status": "Missing argument"}

        existing_user = local_session.query(User).filter(User.login_name == new_username).first()
        if existing_user is not None:
            print("Func: update_user. Error: Already an account with this username")
            return False, {"status": "Username already taken"}

        self.login_name = new_username
        local_session.commit()
        # print("Username Updated")
        return True, {"status": "Username updated"}


    def add_group(self, group_name):

        from augur.util.repo_load_controller import RepoLoadController
            
        local_session = get_session()

        repo_load_controller = RepoLoadController(gh_session=local_session)

        result = repo_load_controller.add_user_group(self.user_id, group_name)

        return result

    def remove_group(self, group_name):

        from augur.util.repo_load_controller import RepoLoadController
        
        local_session = get_session()

        repo_load_controller = RepoLoadController(gh_session=local_session)

        result = repo_load_controller.remove_user_group(self.user_id, group_name)

        return result

    def add_repo(self, group_name, repo_url):
        
        from augur.tasks.github.util.github_task_session import GithubTaskSession
        from augur.util.repo_load_controller import RepoLoadController

        with GithubTaskSession(logger) as session:

            repo_load_controller = RepoLoadController(gh_session=session)

            result = repo_load_controller.add_frontend_repo(repo_url, self.user_id, group_name)

            return result

    def remove_repo(self, group_name, repo_id):
        
        from augur.util.repo_load_controller import RepoLoadController

        local_session = get_session()

        repo_load_controller = RepoLoadController(gh_session=local_session)

        result = repo_load_controller.remove_frontend_repo(repo_id, self.user_id, group_name)
        print(result)

        return result

    def add_org(self, group_name, org_url):
        
        from augur.tasks.github.util.github_task_session import GithubTaskSession
        from augur.util.repo_load_controller import RepoLoadController

        with GithubTaskSession(logger) as session:

            repo_load_controller = RepoLoadController(gh_session=session)

            result = repo_load_controller.add_frontend_org(org_url, self.user_id, group_name)

            return result

    def get_groups(self):
        
        from augur.util.repo_load_controller import RepoLoadController

        local_session = get_session()

        controller = RepoLoadController(local_session)

        user_groups = controller.get_user_groups(self.user_id)

        return user_groups, {"status": "success"}

    def get_group_names(self):

        user_groups = self.get_groups()[0]

        group_names = [group.name for group in user_groups]

        return group_names, {"status": "success"}


    def get_repos(self, page=0, page_size=25, sort="repo_id", direction="ASC"):

        from augur.util.repo_load_controller import RepoLoadController

        local_session = get_session()

        result = RepoLoadController(local_session).paginate_repos("user", page, page_size, sort, direction, user=self)

        return result

    def get_repo_count(self):

        from augur.util.repo_load_controller import RepoLoadController

        local_session = get_session()

        controller = RepoLoadController(local_session)

        result = controller.get_repo_count(source="user", user=self)

        return result


    def get_group_repos(self, group_name, page=0, page_size=25, sort="repo_id", direction="ASC"):

        from augur.util.repo_load_controller import RepoLoadController

        local_session = get_session()

        print("Get group repos")

        result = RepoLoadController(local_session).paginate_repos("group", page, page_size, sort, direction, user=self, group_name=group_name)

        return result


    def get_group_repo_count(self, group_name):
        
        from augur.util.repo_load_controller import RepoLoadController

        local_session = get_session()

        controller = RepoLoadController(local_session)

        result = controller.get_repo_count(source="group", group_name=group_name, user=self)

        return result

    def invalidate_session(self, token):

        from augur.application.db.session import DatabaseSession

        with DatabaseSession(logger) as session:

                row_count = session.query(UserSessionToken).filter(UserSessionToken.user_id == self.user_id, UserSessionToken.token == token).delete()
                session.commit()

        return row_count == 1

    def delete_app(self, app_id):

        from augur.application.db.session import DatabaseSession

        with DatabaseSession(logger) as session:

                row_count = session.query(ClientApplication).filter(ClientApplication.user_id == self.user_id, ClientApplication.id == app_id).delete()
                session.commit()

        return row_count == 1

    def add_app(self, name, redirect_url):

        from augur.application.db.session import DatabaseSession

        with DatabaseSession(logger) as session:

            try:
                app = ClientApplication(id=secrets.token_hex(16), api_key=secrets.token_hex(), name=name, redirect_url=redirect_url, user_id=self.user_id)
                session.add(app)
                session.commit()
            except Exception as e:
                print(e)
                return False

        return True

    def toggle_group_favorite(self, group_name):

        local_session = get_session()

        group = local_session.query(UserGroup).filter(UserGroup.name == group_name, UserGroup.user_id == self.user_id).first()
        if not group:
            return False, {"status": "Group does not exist"}

        group.favorited = not group.favorited

        local_session.commit()

        return True, {"status": "Success"}

    def get_favorite_groups(self):

        local_session = get_session()

        try:
            groups = local_session.query(UserGroup).filter(UserGroup.user_id == self.user_id, UserGroup.favorited == True).all()
        except Exception as e:
            print(f"Error while trying to get favorite groups: {e}")
            return None, {"status": "Error when trying to get favorite groups"}

        return groups, {"status": "Success"}



class UserGroup(Base):
    group_id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, 
                    ForeignKey("augur_operations.users.user_id", name="user_group_user_id_fkey")
    )
    name = Column(String, nullable=False)
    favorited = Column(Boolean, nullable=False, server_default=text("FALSE"))
    __tablename__ = 'user_groups'
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='user_group_unique'),
        {"schema": "augur_operations"}
    )

    user = relationship("User")
    repos = relationship("UserRepo")



class UserRepo(Base):
    __tablename__ = "user_repos"
    __table_args__ = (
        {
            "schema": "augur_operations"
        }
    )

    group_id = Column(
        ForeignKey("augur_operations.user_groups.group_id", name="user_repo_group_id_fkey"), primary_key=True, nullable=False
    )
    repo_id = Column(
        ForeignKey("augur_data.repo.repo_id", name="user_repo_user_id_fkey"), primary_key=True, nullable=False
    )

    repo = relationship("Repo")
    group = relationship("UserGroup")

class UserSessionToken(Base):
    __tablename__ = "user_session_tokens"
    __table_args__ = (
        {
            "schema": "augur_operations"
        }
    )

    token = Column(String, primary_key=True, nullable=False)
    user_id = Column(ForeignKey("augur_operations.users.user_id", name="user_session_token_user_id_fkey"))
    expiration = Column(BigInteger)
    application_id = Column(ForeignKey("augur_operations.client_applications.id", name="user_session_token_application_id_fkey"), nullable=False)
    created_at = Column(BigInteger)

    user = relationship("User")
    application = relationship("ClientApplication")
    refresh_tokens = relationship("RefreshToken")

    @staticmethod
    def create(user_id, application_id, seconds_to_expire=86400):
        import time 

        user_session_token = secrets.token_hex()
        expiration = int(time.time()) + seconds_to_expire
        
        local_session = get_session()
        user_session = UserSessionToken(token=user_session_token, user_id=user_id, application_id = application_id, expiration=expiration)

        local_session.add(user_session)
        local_session.commit()

        return user_session

    def delete_refresh_tokens(self, session):

        refresh_tokens = self.refresh_tokens
        for token in refresh_tokens:
            session.delete(token)
        session.commit()

        session.delete(self)
        session.commit()

class ClientApplication(Base):
    __tablename__ = "client_applications"
    __table_args__ = (
        {
            "schema": "augur_operations"
        }
    )

    id = Column(String, primary_key=True, nullable=False)
    user_id = Column(ForeignKey("augur_operations.users.user_id", name="client_application_user_id_fkey"), nullable=False)
    name = Column(String, nullable=False)
    redirect_url = Column(String, nullable=False)
    api_key = Column(String, nullable=False)

    user = relationship("User")
    sessions = relationship("UserSessionToken")
    subscriptions = relationship("Subscription")

    @staticmethod
    def get_by_id(client_id):

        local_session = get_session()

        return local_session.query(ClientApplication).filter(ClientApplication.id == client_id).first()


class Subscription(Base):
    __tablename__ = "subscriptions"
    __table_args__ = (
        {
            "schema": "augur_operations"
        }
    )

    application_id = Column(ForeignKey("augur_operations.client_applications.id", name="subscriptions_application_id_fkey"), primary_key=True)
    type_id = Column(ForeignKey("augur_operations.subscription_types.id", name="subscriptions_type_id_fkey"), primary_key=True)

    application = relationship("ClientApplication")
    type = relationship("SubscriptionType")

class SubscriptionType(Base):
    __tablename__ = "subscription_types"
    __table_args__ = (
        UniqueConstraint('name', name='subscription_type_title_unique'),
        {"schema": "augur_operations"}
    )


    id = Column(BigInteger, primary_key=True)
    name = Column(String, nullable=False)

    subscriptions = relationship("Subscription")


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"
    __table_args__ = (
        UniqueConstraint('user_session_token', name='refresh_token_user_session_token_id_unique'),
        {"schema": "augur_operations"}
    )

    id = Column(String, primary_key=True)
    user_session_token = Column(ForeignKey("augur_operations.user_session_tokens.token", name="refresh_token_session_token_id_fkey"), nullable=False)

    user_session = relationship("UserSessionToken")

    @staticmethod
    def create(user_session_token_id):

        refresh_token_id = secrets.token_hex()

        local_session = get_session()
        refresh_token = RefreshToken(id=refresh_token_id, user_session_token=user_session_token_id)

        local_session.add(refresh_token)
        local_session.commit()

        return refresh_token


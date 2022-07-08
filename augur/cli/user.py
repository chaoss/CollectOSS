'''
Todo: augur user add <username>
augur user update <username> (On hold for now)
augur user remove <username> (Might not be reqd -Sean)
'''

import os
from flask import Flask
import click
from flask_sqlalchemy import SQLAlchemy 
#from flask_bcrypt import Bcrypt
from uuid import uuid4

app = Flask(__name__)

# SQLAlchemy Settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  
# SQLAlchemy interface                                                               
db = SQLAlchemy (app)
db.app = app 
db.init_app(app)
db.create_all(app=app)

#User Class
class User(db.Model):
    """User model for storing login credentials and other details."""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    #password_hash = db.Column(db.String(100), nullable=False)
    admin = db.Column(db.Boolean, default=False)
    public_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()))

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)

    def __repr__(self):
        return (
            f"<User username={self.username}, public_id={self.public_id}, admin={self.admin}>"
        )

@click.group('user', short_help='Add user utilities')
def cli():
    pass
@cli.command('add', short_help="Add a new user")
@click.argument("username")
@click.option(
    "--admin", is_flag=True, default=False, help="New user has administrator role"
)
@click.password_option(help="Set password")
def add_user(username, admin, password):
    """Add a new user to the database with username."""
    new_user = User(username=username, admin=admin)
    db.session.add(new_user)
    db.session.commit()
    user_type = "admin user" if admin else "user"
    message = f"Successfully added new {user_type}:\n {new_user}"
    click.secho(message, fg="blue", bold=True)
    return 0
'''Next step: password hashing and login using email'''
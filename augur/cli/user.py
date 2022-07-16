'''
Todo: augur user add <username>
augur user update <username> (On hold for now)
augur user remove <username> (Might not be reqd -Sean)
'''

import os
from flask import Flask
import click
from flask_sqlalchemy import SQLAlchemy 
from werkzeug.security import generate_password_hash
from uuid import uuid4

app = Flask(__name__)

# SQLAlchemy Settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3' 
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  
# Construct the DB Object (SQLAlchemy interface)                                                                  
db = SQLAlchemy (app)
db.app = app 
db.init_app(app)

#User Class
class User(db.Model):
    """User model for storing login credentials and other details."""

    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column('password' , db.String(250))
    admin = db.Column(db.Boolean, default=False)
    public_id = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()))

    def __init__(self , username ,password , email, admin):
        self.username = username
        self.set_password(password)
        self.email = email
        self.admin = admin
    
    def set_password(self , password):
        self.password = generate_password_hash(password)
    def __repr__(self):
            return '%r' % (self.username)

#create user table
db.create_all()

#user subcommand
@click.group('user', short_help='Support for adding regular users or administrative users')
def cli():
    pass
@cli.command('add', short_help="Add a new user")
@click.argument("username")
@click.argument("email")
@click.option(
    "--admin", is_flag=True, default=False, help="New user has administrator role"
)
@click.password_option(help="Set password")
def add_user(username, email, admin, password):
    """Add a new user to the database with email address = EMAIL."""
    if User.query.filter(User.username == username).first() is not None:
        return click.echo("username already taken")
    if User.query.filter(User.email == email).first() is not None:
        return click.echo("email already signed-up")
    user = User.query.filter_by(username=username).first()
    if not user:
        new_user = User(username=username, email=email, password=password, admin=admin)
        db.session.add(new_user)
        db.session.commit()
        user_type = "admin user" if admin else "user"
        message = f"Successfully added new {user_type}:\n {new_user}"
        click.secho(message, fg="blue", bold=True)
        return 0
'''Next step: admin model'''
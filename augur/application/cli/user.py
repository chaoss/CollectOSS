'''
Augur commands for adding regular users or administrative users
Add Regular user command: augur user add <username> <email>
Add Admin command: augur user add <username> <email> --admin 
'''

import os
import click
import logging
from werkzeug.security import generate_password_hash
from sqlalchemy.orm import Session
from augur.application.db.engine import create_database_engine


logger = logging.getLogger(__name__)

#user subcommand
@click.group('user', short_help='Support for adding regular users or administrative users')
def cli():
    pass
@cli.command('add', short_help="Add a new user")
@click.argument("username")
@click.argument("email")
@click.argument("firstname")
@click.argument("lastname")
@click.option(
    "--phone-number", default=None, help="User phone number"
)
@click.option(
    "--admin", is_flag=True, default=False, help="New user has administrator role"
)
@click.password_option(help="Set password")
def add_user(username, email, firstname, lastname, phone_number, admin, password):
    """Add a new user to the database with email address = EMAIL."""

    session = Session(create_database_engine())

    if session.query(User).filter(User.login_name == username).first() is not None:
        return click.echo("username already taken")

    if session.query(User).filter(User.email == email).first() is not None:
        return click.echo("email already signed-up")

    user = session.query(User).filter(User.login_name == username).first()
    if not user:
        password = generate_password_hash(password)
        new_user = User(login_name=username, login_hashword=password, email=email, text_phone=phone_number, first_name=firstname, last_name=lastname, admin=admin, tool_source="User CLI", tool_version=None, data_source="CLI")
        db.session.add(new_user)
        db.session.commit()
        user_type = "admin user" if admin else "user"
        message = f"Successfully added new {user_type}: {new_user}"
        click.secho(message, bold=True)
        return 0
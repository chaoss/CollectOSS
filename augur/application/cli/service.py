'''
Augur commands for enabling and disabling services
Running the script:
Enable a service: augur service enable <service>
Disable a service: augur service disable <service>
Check enabled service(s): augur service get-enabled [service]
Modify enabled srevice: augur
'''

import os
import click
import logging
from augur.application.db.models import User
from augur.application.db.engine import DatabaseEngine
from augur.application.db.session import DatabaseSession
from augur.application.config import AugurConfig
# from sqlalchemy.orm import sessionmaker


engine = DatabaseEngine().engine
# Session = sessionmaker(bind=engine)

logger = logging.getLogger(__name__)
Session = DatabaseSession(logger, engine)

#user subcommand
@click.group('services', short_help='Support for managing augur services')
def cli():
    pass

email_providers_menu = """Select email provider:
    [0]\tCancel
    [1]\tTwilio SendGrid

"""

email_providers_choices = [ 0, 1 ]

@cli.command('enable', short_help="Enable a service")
@click.argument("service_name")
def enable_service(service_name):
    """Enable external service integration with Augur.

    Available services: <email>
    """
    config = AugurConfig(logger, Session)

    if service_name == "email":
        if config.get_value("service", "email"):
            return click.echo("Email service already enabled. You can only disable or modify an existing service.")
        
        while (choice := click.prompt(email_providers_menu, type=int)) not in email_providers_choices:
            pass
        
        if not choice:
            # Admin entered 0, canceling the operation
            return click.echo("Exiting")
        
        if choice == 1: # Twilio
            info = [
                {
                    "section_name": "service", "setting_name": "email", "value": True, "type": "bool"
                },
                {
                    "section_name": "email.service",
                    "setting_name": "source_email",
                    "value": click.prompt("Enter source email address"),
                    "type": "str"
                },
                {
                    "section_name": "email.service",
                    "setting_name": "provider",
                    "value": "twilio_sendgrid",
                    "type": "str"
                },
                {
                    "section_name": "email.service",
                    "setting_name": "provider_key",
                    "value": click.prompt("Enter Twilio SendGrid API key"),
                    "type": "str"
                }
            ]
        # setting = {
        #     "section_name": section_name, "setting_name": setting_name, "value": value, "type": data_type # optional
        # }
        config.add_or_update_settings(info)

        return click.echo("Configuration successfully updated. It is recommended to restart Augur if it is currently running.")
    
    return click.echo(f"Invalid service name: [{service_name}]")

@cli.command('get-enabled', short_help="List active services")
def enable_service():
    config = AugurConfig(logger, Session)

    services = [service for (service, enabled) in config.get_section("service").items() if enabled]

    click.echo("Active services:")
    return click.echo(f"\t{services}")

@cli.command('disable', short_help="Disable a service")
@click.argument("service_name")
def enable_service(service_name):
    """Disable active services.
    
    Use 'get-enabled' to list active services."""
    config = AugurConfig(logger, Session)

    if not config.get_value("service", service_name):
        return click.echo(f"Service [{service_name}] not available. Use 'get-enabled' to list active services.")
    
    settings = config.get_section(f"{service_name}.service")

    warning = f"""Disabling this service will delete the following configuration options:

    \t{[setting for setting in settings]}

    Are you sure you want to continue?"""
    
    if not click.confirm(warning):
        return click.echo("Exiting")

    config.remove_section(f"{service_name}.service")
    config.add_or_update_settings([{"section_name": "service", "setting_name": service_name, "value": False}])

    return click.echo("Configuration successfully updated.")
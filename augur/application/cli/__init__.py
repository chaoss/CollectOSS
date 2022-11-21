#SPDX-License-Identifier: MIT
import click
from functools import update_wrapper
import os
import sys
import socket
import re
import json

from augur.application.db.engine import create_database_engine
from sqlalchemy.exc import OperationalError 


def test_connection(function_internet_connection):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        usage = re.search(r"Usage:\s(.*)\s\[OPTIONS\]", str(ctx.get_usage())).groups()[0]
        try:
            #try to ping google's dns server
            socket.create_connection(("8.8.8.8",53))
            return ctx.invoke(function_internet_connection, *args, **kwargs)
        except OSError:
            print(f"\n\n{usage} command setup failed\nYou are not connect to the internet. Please connect to the internet to run Augur\n")
            sys.exit()        
        
    return update_wrapper(new_func, function_internet_connection)

def test_db_connection(function_db_connection):
    @click.pass_context
    def new_func(ctx, *args, **kwargs):
        engine = create_database_engine()
        usage = re.search(r"Usage:\s(.*)\s\[OPTIONS\]", str(ctx.get_usage())).groups()[0]
        try:
            engine.connect()
            engine.dispose()
            return ctx.invoke(function_db_connection, *args, **kwargs)
        except OperationalError as e:

            augur_db_environment_var = os.getenv("AUGUR_DB")

            # determine the location to print in error string
            if augur_db_environment_var:
                location = f"the AUGUR_DB environment variable\nAUGUR_DB={os.getenv('AUGUR_DB')}"
            else:
                with open("db.config.json", 'r') as f:
                    db_config = json.load(f)
                    location = f"db.config.json\nYour db.config.json is: {db_config}"
            
            incorrect_values = "host name is" 
            #  determine which value in the database string is causing the error
            if "could not translate host name" in str(e):
                incorrect_values = "host name is" 

            elif "Connection refused" in str(e):
                incorrect_values = "port is"

            elif "password authentication failed for user" in str(e):
                incorrect_values = "username or password are"
                
            elif "database" in str(e) and "does not exist" in str(e):
                incorrect_values = "database name is" 

            else:
                print(f"Database connection error: {e}")

            if incorrect_values:
                print(f"\n\n{usage} command setup failed\nERROR: connecting to database\nHINT: The {incorrect_values} may be incorrectly specified in {location}\n")
                
            engine.dispose()
            sys.exit()
        
    return update_wrapper(new_func, function_db_connection)

# def pass_application(f):
#     @click.pass_context
#     def new_func(ctx, *args, **kwargs):
#         ctx.obj = Application()
#         return ctx.invoke(f, ctx.obj, *args, **kwargs)
#     return update_wrapper(new_func, f)

# def pass_config(f):
#     @click.pass_context
#     def new_func(ctx, *args, **kwargs):
#         ctx.obj = Application(offline_mode=True).config
#         return ctx.invoke(f, ctx.obj, *args, **kwargs)
#     return update_wrapper(new_func, f)

# def pass_logs_dir(f):
#     @click.pass_context
#     def new_func(ctx, *args, **kwargs):
#         config = AugurConfig(ROOT_AUGUR_DIRECTORY)
#         ctx.obj = AugurLogging.get_log_directories(config, reset_logfiles=False)
#         return ctx.invoke(f, ctx.obj, *args, **kwargs)
#     return update_wrapper(new_func, f)

# def initialize_logging(f):
#     def new_func(*args, **kwargs):
#         AugurLogging(reset_logfiles=False)
#         return f(*args, **kwargs)
#     return update_wrapper(new_func, f)
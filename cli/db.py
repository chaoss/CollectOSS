# SPDX-License-Identifier: MIT
from os import walk, chdir, environ, chmod, path
import os
import logging
from sys import exit
import stat
from collections import OrderedDict
from subprocess import call
import random
import string
import csv
import click
import sqlalchemy as s
import pandas as pd
import requests
import json
from sqlalchemy import exc

from augur_db.engine import engine

logger = logging.getLogger(__name__)


@click.group("db", short_help="Database utilities")
def cli():
    pass


@cli.command("add-repos")
@click.argument("filename", type=click.Path(exists=True))
def add_repos(filename):
    """
    Add repositories to Augur's database
    """
    with engine.connect() as connection:
        df = connection.execute(
            s.sql.text("SELECT repo_group_id FROM augur_data.repo_groups")
        )
        repo_group_IDs = [group[0] for group in df.fetchall()]

        insertSQL = s.sql.text(
            """
            INSERT INTO augur_data.repo(repo_group_id, repo_git, repo_status,
            tool_source, tool_version, data_source, data_collection_date)
            VALUES (:repo_group_id, :repo_git, 'New', 'CLI', 1.0, 'Git', CURRENT_TIMESTAMP)
        """
        )

        with open(filename) as upload_repos_file:
            data = csv.reader(upload_repos_file, delimiter=",")
            for row in data:
                logger.info(
                    f"Inserting repo with Git URL `{row[1]}` into repo group {row[0]}"
                )
                if int(row[0]) in repo_group_IDs:
                    result = connection.execute(
                        insertSQL, repo_group_id=int(row[0]), repo_git=row[1]
                    )
                else:
                    logger.warning(
                        f"Invalid repo group id specified for {row[1]}, skipping."
                    )


@cli.command("get-repo-groups")
def get_repo_groups():
    """
    List all repo groups and their associated IDs
    """

    with engine.connect() as connection:
        df = pd.read_sql(
            s.sql.text(
                "SELECT repo_group_id, rg_name, rg_description FROM augur_data.repo_groups"
            ),
            connection,
        )
    print(df)

    return df


@cli.command("add-repo-groups")
@click.argument("filename", type=click.Path(exists=True))
def add_repo_groups(filename):
    """
    Create new repo groups in Augur's database
    """
    with engine.connect() as connection:

        df = pd.read_sql(
            s.sql.text("SELECT repo_group_id FROM augur_data.repo_groups"),
            connection,
        )
        repo_group_IDs = df["repo_group_id"].values.tolist()

        insert_repo_group_sql = s.sql.text(
            """
        INSERT INTO "augur_data"."repo_groups"("repo_group_id", "rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (:repo_group_id, :repo_group_name, '', '', 0, CURRENT_TIMESTAMP, 'Unknown', 'Loaded by user', '1.0', 'Git', CURRENT_TIMESTAMP);
        """
        )

        with open(filename) as create_repo_groups_file:
            data = csv.reader(create_repo_groups_file, delimiter=",")
            for row in data:

                # Handle case where there's a hanging empty row.
                if not row:
                    logger.info("Skipping empty data...")
                    continue

                logger.info(f"Inserting repo group with values {row}...")
                if int(row[0]) not in repo_group_IDs:
                    repo_group_IDs.append(int(row[0]))
                    connection.execute(
                        insert_repo_group_sql,
                        repo_group_id=int(row[0]),
                        repo_group_name=row[1],
                    )
                else:
                    logger.info(
                        f"Repo group with ID {row[1]} for repo group {row[1]} already exists, skipping..."
                    )


@cli.command("add-github-org")
@click.argument("organization_name")
def add_github_org(organization_name):
    """
    Create new repo groups in Augur's database
    """
    org_query_response = requests.get(
        f"https://api.github.com/orgs/{organization_name}"
    ).json()
    if "login" in org_query_response:
        logger.info(f'Organization "{organization_name}" found')
    else:
        logger.fatal(f"No organization with name {organization_name} could be found")
        exit(1)

    all_repos = []
    page = 1
    repo_query_response = None
    headers = {
        "Authorization": "token %s" % augur_app.config.get_value("Database", "key")
    }
    while repo_query_response != []:
        repo_query_response = requests.get(
            org_query_response["repos_url"] + f"?per_page=100&page={page}",
            headers=headers,
        ).json()
        for repo in repo_query_response:
            all_repos.append(repo)
        page += 1

    insert_repo_group_sql = s.sql.text(
        """
    INSERT INTO "augur_data"."repo_groups"("rg_name", "rg_description", "rg_website", "rg_recache", "rg_last_modified", "rg_type", "tool_source", "tool_version", "data_source", "data_collection_date") VALUES (:repo_group_name, '', '', 0, CURRENT_TIMESTAMP, 'Unknown', 'Loaded by user', '1.0', 'Git', CURRENT_TIMESTAMP) RETURNING repo_group_id;
    """
    )

    with engine.connect() as connection:

        new_repo_group_id = connection.execute(
            insert_repo_group_sql, repo_group_name=organization_name
        ).fetchone()[0]

        insert_repo_sql = s.sql.text(
            """
            INSERT INTO augur_data.repo(repo_group_id, repo_git, repo_status,
            tool_source, tool_version, data_source, data_collection_date)
            VALUES (:repo_group_id, :repo_git, 'New', 'CLI', 1.0, 'Git', CURRENT_TIMESTAMP)
        """
        )
        logger.info(f"{organization_name} repo group created")

        for repo in all_repos:
            logger.info(f"Adding {organization_name}/{repo['name']} ({repo['clone_url']})")
            result = connection.execute(
                insert_repo_sql, repo_group_id=new_repo_group_id, repo_git=repo["clone_url"]
            )


# get_db_version is a helper function to print_db_version and upgrade_db_version
def get_db_version():

    db_version_sql = s.sql.text(
        """
        SELECT * FROM augur_operations.augur_settings WHERE setting = 'augur_data_version'
        """
    )

    with engine.connect() as connection:

        return int(connection.execute(db_version_sql).fetchone()[2])


@cli.command("print-db-version")
# @pass_application
def print_db_version():
    """
    Get the version of the configured database
    """
    call(["alembic", "current"])


@cli.command("upgrade-db-version")
# @pass_application
def upgrade_db_version():
    """
    Upgrade the configured database to the latest version
    """
    call(["alembic", "upgrade", "head"])


@cli.command("check-for-upgrade")
# @pass_application
def check_for_upgrade():
    """
    Upgrade the configured database to the latest version
    """
    call(["alembic", "history", "-i"])


@cli.command("create-schema")
# @pass_application
def create_schema():
    """
    Create schema in the configured database
    """
    call(["alembic", "upgrade", "head"])


def generate_key(length):
    return "".join(
        random.choice(string.ascii_letters + string.digits) for _ in range(length)
    )


@cli.command("generate-api-key")
@click.pass_context
def generate_api_key(ctx):
    """
    Generate and set a new Augur API key
    """
    key = generate_key(32)
    ctx.invoke(update_api_key, api_key=key)
    print(key)


@cli.command("update-api-key")
@click.argument("api_key")
def update_api_key(api_key):
    """
    Update the API key in the database to the given key
    """
    update_api_key_sql = s.sql.text(
        """
        INSERT INTO augur_operations.augur_settings (setting,VALUE) VALUES ('augur_api_key','HudMhTyPW7wiaWopUKgRoGCxlIUulw4g') ON CONFLICT (setting)
        DO
        UPDATE
        SET VALUE='HudMhTyPW7wiaWopUKgRoGCxlIUulw4g';
        --UPDATE augur_operations.augur_settings SET VALUE = :api_key WHERE setting='augur_api_key';
    """
    )

    with engine.connect() as connection:

        augur_app.database.execute(update_api_key_sql, api_key=api_key)
        logger.info(f"Updated Augur API key to: {api_key}")


@cli.command("get-api-key")
def get_api_key():
    get_api_key_sql = s.sql.text(
        """
        SELECT value FROM augur_operations.augur_settings WHERE setting='augur_api_key';
    """
    )

    try:
        with engine.connect() as connection:
            print(connection.execute(get_api_key_sql).fetchone()[0])
    except TypeError:
        logger.error("No Augur API key found.")


@cli.command(
    "check-pgpass",
    short_help="Check the ~/.pgpass file for Augur's database credentials",
)
def check_pgpass():
    print("checking pg-pass")
    if os.path.exists("db.json"):
        with open("db.json", "r") as f:
            config = json.load(f)
            print(f"Config: {config}")
            check_pgpass_credentials(config)
    else:
        db_string = os.getenv("AUGUR_DB")

        db_string_array = db_string.split("@")

        user_and_pass = db_string_array[0].split("/")[2].split(":")

        user = user_and_pass[0]
        password = user_and_pass[1]

        host_port_db_name = db_string_array[1]

        db_name = host_port_db_name.split("/")[1]

        host_and_port = host_port_db_name.split("/")[0].split(":")

        host = host_and_port[0]
        port = host_and_port[1]

        db_config = {
            "user": user,
            "password": password,
            "host": host,
            "port": port,
            "database_name": database_name 
        }

        check_pgpass_credentials(db_config)


@cli.command("init-database")
@click.option("--default-db-name", default="postgres")
@click.option("--default-user", default="postgres")
@click.option("--default-password", default="postgres")
@click.option("--target-db-name", default="augur")
@click.option("--target-user", default="augur")
@click.option("--target-password", default="augur")
@click.option("--host", default="localhost")
@click.option("--port", default="5432")
def init_database(
    default_db_name,
    default_user,
    default_password,
    target_db_name,
    target_user,
    target_password,
    host,
    port,
):
    """
    Create database with the given credentials using the given maintenance database
    """
    config = {
        "Database": {
            "name": default_db_name,
            "user": default_user,
            "password": default_password,
            "host": host,
            "port": port,
        }
    }
    check_pgpass_credentials(config)
    run_db_creation_psql_command(
        host, port, default_user, default_db_name, f"CREATE DATABASE {target_db_name};"
    )
    run_db_creation_psql_command(
        host,
        port,
        default_user,
        default_db_name,
        f"CREATE USER {target_user} WITH ENCRYPTED PASSWORD '{target_password}';",
    )
    run_db_creation_psql_command(
        host,
        port,
        default_user,
        default_db_name,
        f"ALTER DATABASE {target_db_name} OWNER TO {target_user};",
    )
    run_db_creation_psql_command(
        host,
        port,
        default_user,
        default_db_name,
        f"GRANT ALL PRIVILEGES ON DATABASE {target_db_name} TO {target_user};",
    )


def run_db_creation_psql_command(host, port, user, name, command):
    call(
        [
            "psql",
            "-h",
            host,
            "-p",
            port,
            "-U",
            user,
            "-d",
            name,
            "-a",
            "-w",
            "-c",
            command,
        ]
    )


def run_psql_command_in_database(augur_app, target_type, target):
    if target_type not in ["-f", "-c"]:
        logger.error("Invalid target type. Exiting...")
        exit(1)

    call(
        [
            "psql",
            "-h",
            augur_app.config.get_value("Database", "host"),
            "-d",
            augur_app.config.get_value("Database", "name"),
            "-U",
            augur_app.config.get_value("Database", "user"),
            "-p",
            str(augur_app.config.get_value("Database", "port")),
            "-a",
            "-w",
            target_type,
            target,
        ]
    )


def check_pgpass_credentials(config):
    pgpass_file_path = environ["HOME"] + "/.pgpass"

    if not path.isfile(pgpass_file_path):
        logger.info("~/.pgpass does not exist, creating.")
        open(pgpass_file_path, "w+")
        chmod(pgpass_file_path, stat.S_IWRITE | stat.S_IREAD)

    pgpass_file_mask = oct(os.stat(pgpass_file_path).st_mode & 0o777)

    if pgpass_file_mask != "0o600":
        logger.info("Updating ~/.pgpass file permissions.")
        chmod(pgpass_file_path, stat.S_IWRITE | stat.S_IREAD)

    with open(pgpass_file_path, "a+") as pgpass_file:
        end = pgpass_file.tell()
        pgpass_file.seek(0)

        credentials_string = (
            str(config["host"])
            + ":"
            + str(config["port"])
            + ":"
            + str(config["database_name"])
            + ":"
            + str(config["user"])
            + ":"
            + str(config["password"])
        )

        if credentials_string.lower() not in [
            "".join(line.split()).lower() for line in pgpass_file.readlines()
        ]:
            logger.info("Adding credentials to $HOME/.pgpass")
            pgpass_file.seek(end)
            pgpass_file.write(credentials_string + "\n")
        else:
            logger.info("Credentials found in $HOME/.pgpass")

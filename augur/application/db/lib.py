import sqlalchemy as s
import logging
from sqlalchemy.exc import DataError
from typing import List, Any, Optional
from augur.application.db.models import Config, Repo, Commit
from augur.application.db import get_session, get_engine
from augur.application.db.util import execute_session_query

logger = logging.getLogger("db_lib")

def convert_type_of_value(config_dict, logger=None):
        
        
    data_type = config_dict["type"]

    if data_type == "str" or data_type is None:
        return config_dict

    elif data_type == "int":
        config_dict["value"] = int(config_dict["value"])

    elif data_type == "bool":
        value = config_dict["value"]
        
        if value.lower() == "false":
            config_dict["value"] = False
        else:
            config_dict["value"] = True

    elif data_type == "float":
        config_dict["value"] = float(config_dict["value"])

    else:
        if logger:
            logger.error(f"Need to add support for {data_type} types to config") 
        else:
            print(f"Need to add support for {data_type} types to config")

    return config_dict


def get_section(section_name) -> dict:
    """Get a section of data from the config.

    Args:
        section_name: The name of the section being retrieved

    Returns:
        The section data as a dict
    """
    with get_session() as session:

        query = session.query(Config).filter_by(section_name=section_name)
        section_data = execute_session_query(query, 'all')
        
        section_dict = {}
        for setting in section_data:
            setting_dict = setting.__dict__

            setting_dict = convert_type_of_value(setting_dict, logger)

            setting_name = setting_dict["setting_name"]
            setting_value = setting_dict["value"]

            section_dict[setting_name] = setting_value

        return section_dict


def get_value(section_name: str, setting_name: str) -> Optional[Any]:
    """Get the value of a setting from the config.

    Args:
        section_name: The name of the section that the setting belongs to 
        setting_name: The name of the setting

    Returns:
        The value from config if found, and None otherwise
    """

    with get_session() as session:


        # TODO temporary until added to the DB schema
        if section_name == "frontend" and setting_name == "pagination_offset":
            return 25

        try:
            query = session.query(Config).filter(Config.section_name == section_name, Config.setting_name == setting_name)
            config_setting = execute_session_query(query, 'one')
        except s.orm.exc.NoResultFound:
            return None

        setting_dict = config_setting.__dict__

        setting_dict = convert_type_of_value(setting_dict, logger)

        return setting_dict["value"]
    
    
def execute_sql(sql_text):

    engine = get_engine()

    with engine.begin() as connection:

        return_data = connection.execute(sql_text)  

    return return_data

def fetchall_data_from_sql_text(sql_text):

    engine = get_engine()

    with engine.begin() as connection:

        result = connection.execute(sql_text)
    return [dict(row) for row in result.mappings()]

def get_repo_by_repo_git(repo_git: str):

    with get_session() as session:

        query = session.query(Repo).filter(Repo.repo_git == repo_git)
        repo = execute_session_query(query, 'one')

        return repo
    
def get_repo_by_repo_id(repo_id):

    with get_session() as session:

        query = session.query(Repo).filter(Repo.repo_id == repo_id)
        repo = execute_session_query(query, 'one')

        return repo
    
def remove_working_commits_by_repo_id_and_hashes(repo_id, commit_hashes):

    remove_working_commits = s.sql.text("""DELETE FROM working_commits 
        WHERE repos_id = :repo_id AND working_commit IN :hashes
        """).bindparams(repo_id=repo_id,hashes=tuple(commit_hashes))
    
    execute_sql(remove_working_commits)  

def remove_working_commits_by_repo_id(repo_id):

    remove_working_commits = s.sql.text("""DELETE FROM working_commits WHERE repos_id=:repo_id""").bindparams(repo_id=repo_id)
    execute_sql(remove_working_commits)

def remove_commits_by_repo_id_and_hashes(repo_id, commit_hashes):

    remove_commit = s.sql.text("""DELETE FROM commits
        WHERE repo_id=:repo_id
        AND cmt_commit_hash IN :hashes""").bindparams(repo_id=repo_id,hashes=tuple(commit_hashes))
    execute_sql(remove_commit)


def remove_commits_by_repo_id(repo_id):

    remove_commits = s.sql.text("""DELETE FROM commits WHERE repo_id=:repo_id""").bindparams(repo_id=repo_id)
    execute_sql(remove_commits) 

def get_working_commits_by_repo_id(repo_id):

    query = s.sql.text("""SELECT working_commit FROM working_commits WHERE repos_id=:repo_id
    """).bindparams(repo_id=repo_id)

    try:
        working_commits = fetchall_data_from_sql_text(query)
    except:
        working_commits = []

    return working_commits


def facade_bulk_insert_commits(logger, records):

    with get_session() as session:

        try:
            session.execute(
                    s.insert(Commit),
                    records,
                )
            session.commit()
        except Exception as e:
            
            if len(records) > 1:
                logger.error(f"Ran into issue when trying to insert commits \n Error: {e}")

                #split list into halves and retry insert until we isolate offending record
                firsthalfRecords = records[:len(records)//2]
                secondhalfRecords = records[len(records)//2:]

                facade_bulk_insert_commits(logger, session,firsthalfRecords)
                facade_bulk_insert_commits(logger, session,secondhalfRecords)
            elif len(records) == 1 and isinstance(e,DataError) and "time zone displacement" in f"{e}":
                commit_record = records[0]
                #replace incomprehensible dates with epoch.
                #2021-10-11 11:57:46 -0500
                placeholder_date = "1970-01-01 00:00:15 -0500"

                #Check for improper utc timezone offset
                #UTC timezone offset should be betwen -14:00 and +14:00

                commit_record['author_timestamp'] = placeholder_date
                commit_record['committer_timestamp'] = placeholder_date

                session.execute(
                    s.insert(Commit),
                    [commit_record],
                )
                session.commit()
            else:
                raise e




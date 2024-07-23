import time
import random
import logging
import sqlalchemy as s
from sqlalchemy import func 
from sqlalchemy.exc import DataError
from sqlalchemy.dialects import postgresql
from sqlalchemy.exc import OperationalError
from psycopg2.errors import DeadlockDetected
from typing import List, Any, Optional, Union

from augur.application.db.models import Config, Repo, Commit, WorkerOauth, Issue, PullRequest, PullRequestReview, ContributorsAlias,UnresolvedCommitEmail, Contributor, CollectionStatus
from augur.tasks.util.collection_state import CollectionState
from augur.application.db import get_session, get_engine
from augur.application.db.util import execute_session_query
from augur.application.db.session import remove_duplicates_by_uniques, remove_null_characters_from_list_of_dicts

logger = logging.getLogger("db_lib")

def convert_type_of_value(config_dict, logger=None):
        
        
    data_type = config_dict["type"]

    if data_type == "str" or data_type is None:
        return config_dict

    if data_type == "int":
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

def get_worker_oauth_keys(platform: str):

    with get_session() as session:

        results = session.query(WorkerOauth).filter(WorkerOauth.platform == platform).order_by(func.random()).all()

        return [row.access_token for row in results]
    
def get_active_repo_count(collection_type):

    with get_session() as session:
    
        return session.query(CollectionStatus).filter(getattr(CollectionStatus,f"{collection_type}_status" ) == CollectionState.COLLECTING.value).count()


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

                facade_bulk_insert_commits(logger, firsthalfRecords)
                facade_bulk_insert_commits(logger, secondhalfRecords)
            elif len(records) == 1 and isinstance(e,DataError) and "time zone displacement" in f"{e}":
                commit_record = records[0]
                #replace incomprehensible dates with epoch.
                #2021-10-11 11:57:46 -0500
                placeholder_date = "1970-01-01 00:00:15 -0500"

                #Check for improper utc timezone offset
                #UTC timezone offset should be between -14:00 and +14:00

                commit_record['author_timestamp'] = placeholder_date
                commit_record['committer_timestamp'] = placeholder_date

                session.execute(
                    s.insert(Commit),
                    [commit_record],
                )
                session.commit()
            else:
                raise e
            

def bulk_insert_dicts(logger, data: Union[List[dict], dict], table, natural_keys: List[str], return_columns: Optional[List[str]] = None, string_fields: Optional[List[str]] = None, on_conflict_update:bool = True) -> Optional[List[dict]]:

    if isinstance(data, list) is False:
        
        # if a dict is passed to data then 
        # convert it to a list with one value
        if isinstance(data, dict) is True:
            data = [data]
        
        else:
            logger.error("Data must be a list or a dict")
            return None

    if len(data) == 0:
        # self.logger.info("Gave no data to insert, returning...")
        return None

    if isinstance(data[0], dict) is False: 
        logger.error("Must be list of dicts")
        return None

    # remove any duplicate data 
    # this only counts something as a duplicate if every field is the same
    data = remove_duplicates_by_uniques(data, natural_keys)

    # remove null data from string fields
    if string_fields and isinstance(string_fields, list):
        data = remove_null_characters_from_list_of_dicts(data, string_fields)

    # creates list of arguments to tell sqlalchemy what columns to return after the data is inserted
    returning_args = []
    if return_columns:
        for column in return_columns:
            argument = getattr(table, column)
            returning_args.append(argument)

    # creates insert on table
    # that returns cols specificed in returning_args
    # and inserts the data specified in data
    # NOTE: if return_columns does not have an values this still works
    stmnt = postgresql.insert(table).returning(*returning_args).values(data)


    if on_conflict_update:

        # create a dict that the on_conflict_do_update method requires to be able to map updates whenever there is a conflict. See sqlalchemy docs for more explanation and examples: https://docs.sqlalchemy.org/en/14/dialects/postgresql.html#updating-using-the-excluded-insert-values
        setDict = {}
        for key in data[0].keys():
                setDict[key] = getattr(stmnt.excluded, key)
            
        stmnt = stmnt.on_conflict_do_update(
            #This might need to change
            index_elements=natural_keys,
            
            #Columns to be updated
            set_ = setDict
        )

    else:
        stmnt = stmnt.on_conflict_do_nothing(
            index_elements=natural_keys
        )


    # print(str(stmnt.compile(dialect=postgresql.dialect())))
    attempts = 0
    # creates list from 1 to 10 / changed to 10-30 because deadlocks are taking longer
    sleep_time_list = list(range(10,30))
    deadlock_detected = False

    engine = get_engine()

    # if there is no data to return then it executes the insert then returns nothing
    if not return_columns:

        while attempts < 10:
            try:
                #begin keyword is needed for sqlalchemy 2.x
                #this is because autocommit support was removed in 2.0
                with engine.begin() as connection:
                    connection.execute(stmnt)
                    break
            except OperationalError as e:
                # print(str(e).split("Process")[1].split(";")[0])
                if isinstance(e.orig, DeadlockDetected):
                    deadlock_detected = True
                    sleep_time = random.choice(sleep_time_list)
                    logger.debug(f"Deadlock detected on {table.__table__} table...trying again in {round(sleep_time)} seconds: transaction size: {len(data)}")
                    time.sleep(sleep_time)

                    attempts += 1
                    continue
                
                raise e

            except Exception as e:
                #self.logger.info(e)
                if len(data) == 1:
                    raise e
                
                time.sleep(3)
                first_half = data[:len(data)//2]
                second_half = data[len(data)//2:]

                bulk_insert_dicts(logger, first_half, table, natural_keys, return_columns, string_fields, on_conflict_update)
                bulk_insert_dicts(logger, second_half,table, natural_keys, return_columns, string_fields, on_conflict_update)

        else:
            logger.error("Unable to insert data in 10 attempts")
            return None

        if deadlock_detected is True:
            logger.error("Made it through even though Deadlock was detected")
                
        return "success"
    

    # othewise it gets the requested return columns and returns them as a list of dicts
    while attempts < 10:
        try:
            with engine.begin() as connection:
                return_data_tuples = connection.execute(stmnt)
                break
        except OperationalError as e:
            if isinstance(e.orig, DeadlockDetected):
                sleep_time = random.choice(sleep_time_list)
                logger.debug(f"Deadlock detected on {table.__table__} table...trying again in {round(sleep_time)} seconds: transaction size: {len(data)}")
                time.sleep(sleep_time)

                attempts += 1
                continue   

            raise e

        except Exception as e:
            if len(data) == 1:
                raise e
            
            time.sleep(3)
            first_half = data[:len(data)//2]
            second_half = data[len(data)//2:]

            bulk_insert_dicts(logger, first_half, table, natural_keys, return_columns, string_fields, on_conflict_update)
            bulk_insert_dicts(logger, second_half, table, natural_keys, return_columns, string_fields, on_conflict_update)

    else:
        logger.error("Unable to insert and return data in 10 attempts")
        return None

    if deadlock_detected is True:
        logger.error("Made it through even though Deadlock was detected")

    return_data = [dict(row) for row in return_data_tuples.mappings()]
    
    #no longer working in sqlalchemy 2.x
    #for data_tuple in return_data_tuples:
    #    return_data.append(dict(data_tuple))

    # using on confilict do nothing does not return the 
    # present values so this does gets the return values
    if not on_conflict_update:

        conditions = []
        for column in natural_keys:

            column_values = [value[column] for value in data]

            column = getattr(table, column)

            conditions.append(column.in_(tuple(column_values)))

        with get_session() as session:

            result = (
                session.query(table).filter(*conditions).all()
            )

        for row in result:

            return_dict = {}
            for field in return_columns:

                return_dict[field] = getattr(row, field)

            return_data.append(return_dict)


    return return_data



def get_issues_by_repo_id(repo_id):

    with get_session() as session:

        return session.query(Issue).filter(Issue.repo_id == repo_id).all()
    
def get_pull_requests_by_repo_id(repo_id):

    with get_session() as session:

        return session.query(PullRequest).filter(PullRequest.repo_id == repo_id).all()
    
def get_pull_request_reviews_by_repo_id(repo_id):

    with get_session() as session:

        return session.query(PullRequestReview).filter(PullRequestReview.repo_id == repo_id).all()
    
def get_contributor_aliases_by_email(email):

    with get_session() as session:

        return session.query(ContributorsAlias).filter_by(alias_email=email).all()
    
def get_unresolved_commit_emails_by_name(name):

    with get_session() as session:

        return session.query(UnresolvedCommitEmail).filter_by(name=name).all()
 
def get_contributors_by_full_name(full_name):

    with get_session() as session:

        return session.query(Contributor).filter_by(cntrb_full_name=full_name).all()
    
def get_contributors_by_github_user_id(id):

    with get_session() as session:

        # Look into this, where it was used was doing .all() but this query should really only return one
        return session.query(Contributor).filter_by(gh_user_id=id).all()

def update_issue_closed_cntrbs_by_repo_id(repo_id):

    engine = get_engine()

    get_ranked_issues = s.text(f"""
        WITH RankedIssues AS (
            SELECT repo_id, issue_id, cntrb_id, 
                ROW_NUMBER() OVER(PARTITION BY issue_id ORDER BY created_at DESC) AS rn
            FROM issue_events 
            WHERE "action" = 'closed'
        )
                                            
        SELECT issue_id, cntrb_id from RankedIssues where rn=1 and repo_id={repo_id} and cntrb_id is not NULL
    """)

    with engine.connect() as conn:
        result = conn.execute(get_ranked_issues).fetchall()

    update_data = []
    for row in result:
        update_data.append(
            {
            'issue_id': row[0], 
            'cntrb_id': row[1], 
            'repo_id': repo_id
            }
        )

    if update_data:
        with engine.connect() as connection:
            update_stmt = s.text("""
                UPDATE issues
                SET cntrb_id = :cntrb_id
                WHERE issue_id = :issue_id
                AND repo_id = :repo_id
            """)
            connection.execute(update_stmt, update_data)

def get_core_data_last_collected(repo_id):
    
    with get_session() as session:
        try:
           return session.query(CollectionStatus).filter(CollectionStatus.repo_id == repo_id).one().core_data_last_collected 
        except s.orm.exc.NoResultFound:
            return None

def get_secondary_data_last_collected(repo_id):
    
    with get_session() as session:
        try:
           return session.query(CollectionStatus).filter(CollectionStatus.repo_id == repo_id).one().secondary_data_last_collected 
        except s.orm.exc.NoResultFound:
            return None
        
def get_updated_prs(repo_id, since):
    
    with get_session() as session:
        return session.query(PullRequest).filter(PullRequest.repo_id == repo_id, PullRequest.pr_updated_at >= since).order_by(PullRequest.pr_src_number).all()
    
def get_updated_issues(repo_id, since):

    with get_session() as session:
        return session.query(Issue).filter(Issue.repo_id == repo_id, Issue.updated_at >= since).order_by(Issue.gh_issue_number).all()
            

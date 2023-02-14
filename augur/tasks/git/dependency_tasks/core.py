from datetime import datetime
import logging
import requests
import json
import traceback
from augur.application.db.data_parse import *
from augur.application.db.models import *
from augur.application.db.session import DatabaseSession
from augur.application.config import AugurConfig
from augur.application.db.util import execute_session_query
from augur.tasks.git.dependency_tasks.dependency_util import dependency_calculator as dep_calc

def generate_deps_data(session, repo_id, path):
        """Runs scc on repo and stores data in database
        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """
        
        session.logger.info('Searching for deps in repo')
        session.logger.info(f'Repo ID: {repo_id}, Path: {path}')

        deps = dep_calc.get_deps(path)
        try: 
            for dep in deps:
                    repo_deps = {
                        'repo_id': repo_id,
                        'dep_name' : dep.name,
    	                'dep_count' : dep.count,
    	                'dep_language' : dep.language,
                        'tool_source': 'deps_model',
                        'tool_version': '0.43.9',
                        'data_source': 'Git',
                        'data_collection_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
                    }

                    insert_statement = s.sql.text("""
                        INSERT INTO "repo_dependencies" ("repo_id", "dep_name", "dep_count", "dep_language", "tool_source", "tool_version", "data_source", "data_collection_date")
                        VALUES (:repo_id, :dep_name, :dep_count, :dep_language, :tool_source, :tool_version, :data_source, :data_collection_date)
                    """).bindparams(**repo_deps)

                    #result = self.db.execute(self.repo_dependencies_table.insert().values(repo_deps))
                    session.execute_sql(insert_statement)
        except Exception as e:
            session.logger.error(f"Could not complete generate_deps_data!\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")


def deps_model(session, repo_id):
    """ Data collection and storage method
    """
    session.logger.info(f"This is the deps model repo: {repo_id}.")

    repo_path_sql = s.sql.text("""
        SELECT repo_id, CONCAT(repo_group_id || chr(47) || repo_path || repo_name) AS path
        FROM repo
        WHERE repo_id = :repo_id
    """).bindparams(repo_id=repo_id)

    result = session.execute_sql(repo_path_sql)
    
    relative_repo_path = result.fetchone()[1]
    config = AugurConfig(session.logger, session)
    absolute_repo_path = config.get_section("Facade")['repo_directory'] + relative_repo_path

    try:
        generate_deps_data(session,repo_id, absolute_repo_path)
    except Exception as e:
        session.logger.error(f"Could not complete deps_model!\n Reason: {e} \n Traceback: {''.join(traceback.format_exception(None, e, e.__traceback__))}")
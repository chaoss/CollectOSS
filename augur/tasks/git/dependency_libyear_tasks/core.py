from datetime import datetime
import logging
import requests
import re
import os, subprocess
import traceback
import sqlalchemy as s
from augur.application.db.models import *
from augur.application.db.session import DatabaseSession
from augur.application.config import AugurConfig
from augur.application.db.util import execute_session_query
from urllib.parse import quote
from augur.tasks.git.dependency_libyear_tasks.libyear_util.util import get_deps_libyear_data

def deps_libyear_model( session, repo_id,repo_git,repo_group_id):
        """ Data collection and storage method
        """
        session.logger.info(f"This is the libyear deps model repo: {repo_git}")

        result = re.search(r"https:\/\/(github\.com\/[A-Za-z0-9 \- _]+\/)([A-Za-z0-9 \- _ .]+)$", repo_git).groups()

        relative_repo_path = f"{repo_group_id}/{result[0]}{result[1]}"
        config = AugurConfig(session.logger, session)
        
        absolute_repo_path = config.get_section("Facade")['repo_directory'] + relative_repo_path#self.config['repo_directory'] + relative_repo_path

        generate_deps_libyear_data(session,repo_id, absolute_repo_path)


def generate_deps_libyear_data(session, repo_id, path):
        """Scans for package files and calculates libyear
        :param session: Task manifest and database session. 
        :param repo_id: Repository ID
        :param path: Absolute path of the Repostiory
        """
        date_scanned = datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')
        session.logger.info('Searching for deps in repo')
        session.logger.info(f'Repo ID: {repo_id}, Path: {path}')

        deps = get_deps_libyear_data(path,session.logger)

        if not deps:
            session.logger.info(f"No deps found for repo {repo_id} on path {path}")
            return

        to_insert = []
        for dep in deps:
            repo_deps = {
                'repo_id': repo_id,
                'name' : dep['name'],
                'requirement' : dep['requirement'],
                'type' : dep['type'],
                'package_manager' : dep['package'],
                'current_verion' : dep['current_version'],
                'latest_version' : dep['latest_version'],
                'current_release_date' : dep['current_release_date'],
                'latest_release_date' : dep['latest_release_date'],
                'libyear' : dep['libyear'],
                'tool_source': 'deps_libyear',
                'tool_version': '0.44.3',
                'data_source': 'git',
                'data_collection_date': date_scanned
            }

            #result = self.db.execute(self.repo_deps_libyear_table.insert().values(repo_deps))
            #self.logger.info(f"Added dep: {result.inserted_primary_key}")
            #insert_statement = s.sql.text("""
            #    INSERT INTO "repo_deps_libyear" ("repo_id","name","requirement","type","package_manager","current_verion","latest_version","current_release_date","latest_release_date","libyear","tool_source","tool_version","data_source","data_collection_date")
            #    VALUES (:repo_id, :name,:requirement,:type,:package_manager,:current_verion,:latest_version,:current_release_date,:latest_release_date,:libyear,:tool_source,:tool_version,:data_source, :data_collection_date)
            #""").bindparams(**repo_deps)
#
            #session.execute_sql(insert_statement)
            to_insert.append(repo_deps)
        session.insert_data(to_insert, RepoDepsLibyear, ["repo_id","name","data_collection_date"])

#SPDX-License-Identifier: MIT
"""
Keeps data up to date
"""
import coloredlogs
from copy import deepcopy
import logging, os, time, requests
import logging.config
from multiprocessing import Process, get_start_method
from sqlalchemy.ext.automap import automap_base
import sqlalchemy as s
import pandas as pd
from sqlalchemy import MetaData

from augur.logging import AugurLogging

import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class Housekeeper:

    def __init__(self, broker, augur_app):
        logger.info("Booting housekeeper")

        self._processes = []
        self.augur_logging = augur_app.logging
        self.jobs = deepcopy(augur_app.config.get_value("Housekeeper", "jobs"))
        self.broker_host = augur_app.config.get_value("Server", "host")
        self.broker_port = augur_app.config.get_value("Server", "port")
        self.broker = broker

        self.db = augur_app.database
        self.helper_db = augur_app.operations_database

        helper_metadata = MetaData()
        helper_metadata.reflect(self.helper_db, only=['worker_job'])
        HelperBase = automap_base(metadata=helper_metadata)
        HelperBase.prepare()
        self.job_table = HelperBase.classes.worker_job.__table__

        repoUrlSQL = s.sql.text("""
            SELECT repo_git FROM repo
        """)
        rs = pd.read_sql(repoUrlSQL, self.db, params={})
        all_repos = rs['repo_git'].values.tolist()

        # List of tasks that need periodic updates
        self.schedule_updates()

    def schedule_updates(self):
        """
        Starts update processes
        """
        self.prep_jobs()
        self.augur_logging.initialize_housekeeper_logging_listener()
        logger.info("Scheduling update processes")
        for job in self.jobs:
            process = Process(target=self.updater_process, name=job["model"], args=(self.broker_host, self.broker_port, self.broker, job, (self.augur_logging.housekeeper_job_config, self.augur_logging.get_config())))
            self._processes.append(process)
            process.start()


    @staticmethod
    def updater_process(broker_host, broker_port, broker, job, logging_config):
        """
        Controls a given plugin's update process

        """
        logging.config.dictConfig(logging_config[0])
        logger = logging.getLogger(f"augur.jobs.{job['model']}")
        coloredlogs.install(level=logging_config[1]["log_level"], logger=logger, fmt=logging_config[1]["format_string"])

        if logging_config[1]["quiet"]:
            logger.disabled

        if 'repo_group_id' in job:
            repo_group_id = job['repo_group_id']
            logger.info('Housekeeper spawned {} model updater process for repo group id {}'.format(job['model'], repo_group_id))
        else:
            repo_group_id = None
            logger.info('Housekeeper spawned {} model updater process for repo ids {}'.format(job['model'], job['repo_ids']))

        try:
            compatible_worker_found = False
            # Waiting for compatible worker
            while True:
                if not compatible_worker_found:
                    for worker in list(broker._getvalue().keys()):
                        if job['model'] in broker[worker]['models'] and job['given'] in broker[worker]['given']:
                            compatible_worker_found = True
                    time.sleep(3)
                    continue

                logger.info("Housekeeper recognized that the broker has a worker that " + 
                    "can handle the {} model... beginning to distribute maintained tasks".format(job['model']))
                while True:
                    logger.info('Housekeeper updating {} model with given {}...'.format(
                        job['model'], job['given'][0]))
                    
                    if job['given'][0] == 'git_url' or job['given'][0] == 'github_url':
                        for repo in job['repos']:
                            if job['given'][0] == 'github_url' and 'github.com' not in repo['repo_git']:
                                continue
                            given_key = 'git_url' if job['given'][0] == 'git_url' else 'github_url'
                            task = {
                                "job_type": job['job_type'] if 'job_type' in job else 'MAINTAIN', 
                                "models": [job['model']], 
                                "display_name": "{} model for url: {}".format(job['model'], repo['repo_git']),
                                "given": {}
                            }
                            task['given'][given_key] = repo['repo_git']
                            if "focused_task" in repo:
                                task["focused_task"] = repo['focused_task']
                            try:
                                requests.post('http://{}:{}/api/unstable/task'.format(
                                    broker_host,broker_port), json=task, timeout=10)
                            except Exception as e:
                                logger.error("Error encountered: {}".format(e))

                            logger.debug(task)

                            time.sleep(15)

                    elif job['given'][0] == 'repo_group':
                        task = {
                                "job_type": job['job_type'] if 'job_type' in job else 'MAINTAIN', 
                                "models": [job['model']], 
                                "display_name": "{} model for repo group id: {}".format(job['model'], repo_group_id),
                                "given": {
                                    "repo_group": job['repos']
                                }
                            }
                        try:
                            requests.post('http://{}:{}/api/unstable/task'.format(
                                broker_host,broker_port), json=task, timeout=10)
                        except Exception as e:
                            logger.error("Error encountered: {}".format(e))

                    logger.info("Housekeeper finished sending {} tasks to the broker for it to distribute to your worker(s)".format(len(job['repos'])))
                    time.sleep(job['delay'])

        except KeyboardInterrupt as e:
            pass

    def join_updates(self):
        """
        Join to the update processes
        """
        for process in self._processes:
            logger.debug(f"Joining {process.name} update process")
            process.join()

    def shutdown_updates(self):
        """
        Ends all running update processes
        """
        for process in self._processes:
            # logger.debug(f"Terminating {process.name} update process")
            process.terminate()

    def prep_jobs(self):
        logger.info("Preparing housekeeper jobs")
        for job in self.jobs:
            if 'repo_group_id' in job or 'repo_ids' in job:
                # If RG id is 0 then it just means to query all repos
                where_and = 'AND' if job['model'] == 'issues' and 'repo_group_id' in job else 'WHERE'
                where_condition = '{} repo_group_id = {}'.format(where_and, job['repo_group_id']
                    ) if 'repo_group_id' in job and job['repo_group_id'] != 0 else '{} repo.repo_id IN ({})'.format(
                    where_and, ",".join(str(id) for id in job['repo_ids'])) if 'repo_ids' in job else ''
                repo_url_sql = s.sql.text("""
                        SELECT
                            * 
                        FROM
                            (
                                ( SELECT repo_git, repo.repo_id, issues_enabled, COUNT ( * ) AS meta_count 
                                FROM repo left outer join repo_info on repo.repo_id = repo_info.repo_id
                                GROUP BY repo.repo_id, issues_enabled 
                                ORDER BY repo.repo_id ) zz
                                LEFT OUTER JOIN (
                                SELECT repo.repo_id,
                                    repo.repo_name,
                                    b.pull_request_count,
                                    d.repo_id AS pull_request_repo_id,
                                    e.last_collected,
                                    (
                                    b.pull_request_count - COUNT ( * )) AS pull_requests_missing,
                                    ABS (
                                    CAST (( COUNT ( * )) AS DOUBLE PRECISION ) / CAST ( b.pull_request_count + 1 AS DOUBLE PRECISION )) AS ratio_abs,
                                    (
                                    CAST (( COUNT ( * )) AS DOUBLE PRECISION ) / CAST ( b.pull_request_count + 1 AS DOUBLE PRECISION )) AS ratio_issues 
                                FROM
                                    augur_data.repo left outer join  
                                    augur_data.pull_requests d on d.repo_id = repo.repo_id left outer join 
                                                                        ( SELECT repo_id, MAX ( data_collection_date ) AS last_collected FROM augur_data.repo_info GROUP BY repo_id ORDER BY repo_id ) e 
                                    on e.repo_id = d.repo_id left outer join 
                                    augur_data.repo_info b on e.repo_id = b.repo_id and b.data_collection_date = e.last_collected
                                {}                      
                                GROUP BY
                                    repo.repo_id,
                                    d.repo_id,
                                    b.pull_request_count,
                                    e.last_collected 
                                ORDER BY ratio_abs
                                ) yy ON zz.repo_id = yy.repo_id 
                            ) D 
                        ORDER BY ratio_abs NULLS FIRST
                    """.format(where_condition)) if job['model'] == 'pull_requests' and 'repo_group_id' in job else s.sql.text("""
                        SELECT
                            * 
                        FROM
                            (
                                ( SELECT repo_git, repo.repo_id, issues_enabled, COUNT ( * ) AS meta_count 
                                FROM repo left outer join repo_info on repo.repo_id = repo_info.repo_id
                                --WHERE issues_enabled = 'true' 
                                GROUP BY repo.repo_id, issues_enabled 
                                ORDER BY repo.repo_id ) zz
                                LEFT OUTER JOIN (
                                SELECT repo.repo_id,
                                    repo.repo_name,
                                    b.issues_count,
                                    d.repo_id AS issue_repo_id,
                                    e.last_collected,
                                    COUNT ( * ) AS issues_collected_count,
                                    (
                                    b.issues_count - COUNT ( * )) AS issues_missing,
                                    ABS (
                                    CAST (( COUNT ( * )) AS DOUBLE PRECISION ) / CAST ( b.issues_count + 1 AS DOUBLE PRECISION )) AS ratio_abs,
                                    (
                                    CAST (( COUNT ( * )) AS DOUBLE PRECISION ) / CAST ( b.issues_count + 1 AS DOUBLE PRECISION )) AS ratio_issues 
                                FROM
                                    augur_data.repo left outer join  
                                    augur_data.pull_requests d on d.repo_id = repo.repo_id left outer join 
                                    augur_data.repo_info b on d.repo_id = b.repo_id left outer join
                                    ( SELECT repo_id, MAX ( data_collection_date ) AS last_collected FROM augur_data.repo_info GROUP BY repo_id ORDER BY repo_id ) e 
                                                                        on e.repo_id = d.repo_id and b.data_collection_date = e.last_collected
                                WHERE d.pull_request_id IS NULL
                                {}
                                GROUP BY
                                    repo.repo_id,
                                    d.repo_id,
                                    b.issues_count,
                                    e.last_collected 
                                ORDER BY ratio_abs 
                                ) yy ON zz.repo_id = yy.repo_id 
                            ) D
                        ORDER BY ratio_abs NULLS FIRST
                    """.format(where_condition)) if job['model'] == 'issues' and 'repo_group_id' in job else s.sql.text(""" 
                        SELECT repo_git, repo_id FROM repo {} ORDER BY repo_id ASC
                    """.format(where_condition)) if 'order' not in job else s.sql.text(""" 
                        SELECT repo_git, repo.repo_id, count(*) as commit_count 
                        FROM augur_data.repo left outer join augur_data.commits 
                            on repo.repo_id = commits.repo_id 
                        {}
                        group by repo.repo_id ORDER BY commit_count {}
                    """.format(where_condition, job['order']))
                
                reorganized_repos = pd.read_sql(repo_url_sql, self.db, params={})
                if len(reorganized_repos) == 0:
                    logger.warning("Trying to send tasks for repo group, but the repo group does not contain any repos: {}".format(repo_url_sql))
                    job['repos'] = []
                    continue

                if 'starting_repo_id' in job:
                    last_id = job['starting_repo_id']
                else:
                    repoIdSQL = s.sql.text("""
                            SELECT since_id_str FROM worker_job
                            WHERE job_model = '{}'
                        """.format(job['model']))

                    job_df = pd.read_sql(repoIdSQL, self.helper_db, params={})

                    # If there is no job tuple found, insert one
                    if len(job_df) == 0:
                        job_tuple = {
                            'job_model': job['model'],
                            'oauth_id': 0
                        }
                        result = self.helper_db.execute(self.job_table.insert().values(job_tuple))
                        logger.debug("No job tuple for {} model was found, so one was inserted into the job table: {}".format(job['model'], job_tuple))

                    # If a last id is not recorded, start from beginning of repos 
                    #   (first id is not necessarily 0)
                    try:
                        last_id = int(job_df.iloc[0]['since_id_str'])
                    except:
                        last_id = 0

                jobHistorySQL = s.sql.text("""
                        SELECT max(history_id) AS history_id, status FROM worker_history
                        GROUP BY status
                        LIMIT 1
                    """)

                history_df = pd.read_sql(jobHistorySQL, self.helper_db, params={})

                finishing_task = False
                if len(history_df.index) != 0:
                    if history_df.iloc[0]['status'] == 'Stopped':
                        self.history_id = int(history_df.iloc[0]['history_id'])
                        finishing_task = True

                # Rearrange repos so the one after the last one that 
                #   was completed will be ran first (if prioritized ordering is not available/enabled)
                if job['model'] not in ['issues', 'pull_requests']:
                    before_repos = reorganized_repos.loc[reorganized_repos['repo_id'].astype(int) < last_id]
                    after_repos = reorganized_repos.loc[reorganized_repos['repo_id'].astype(int) >= last_id]

                    reorganized_repos = after_repos.append(before_repos)

                if 'all_focused' in job:
                    reorganized_repos['focused_task'] = job['all_focused']

                reorganized_repos = reorganized_repos.to_dict('records')
            
                if finishing_task:
                    reorganized_repos[0]['focused_task'] = 1
                
                job['repos'] = reorganized_repos

            elif 'repo_id' in job:
                job['repo_group_id'] = None
                repoUrlSQL = s.sql.text("""
                    SELECT repo_git, repo_id FROM repo WHERE repo_id = {}
                """.format(job['repo_id']))

                rs = pd.read_sql(repoUrlSQL, self.db, params={})

                if 'all_focused' in job:
                    rs['focused_task'] = job['all_focused']

                rs = rs.to_dict('records')

                job['repos'] = rs
            # time.sleep(120)


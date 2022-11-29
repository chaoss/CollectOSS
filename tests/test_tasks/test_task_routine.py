# #SPDX-License-Identifier: MIT
# from augur.tasks.init.celery_app import celery_app as celery
# from augur.tasks.github import *
# import pytest
# from tests.test_tasks.runner import *
# from augur.tasks.start_tasks import *
# from augur.tasks.git.facade_tasks import *


# def test_augur_task_routine_no_dependencies(celery_instance):
#     routine = AugurTaskRoutine()

#     routine['facade'] = facade_commits_model.si()

#     repo_git = 'https://github.com/chaoss/augur/'
#     task_list = []
#     task_list.append(collect_pull_requests.si(repo_git))
#     task_list.append(collect_issues.si(repo_git))
#     routine['prs_and_issues'] = group(task_list)

#     routine.start_data_collection()


# def test_augur_task_routine_with_dependencies(celery_instance):
#     routine = AugurTaskRoutine()

#     routine['facade'] = facade_commits_model.si()

#     repo_git = 'https://github.com/chaoss/augur/'
#     task_list = []
#     task_list.append(collect_pull_requests.si(repo_git))
#     task_list.append(collect_issues.si(repo_git))
#     routine['prs_and_issues'] = group(task_list)

#     routine.add_dependency_relationship(job='prs_and_issues',depends_on='facade')
    
#     routine.start_data_collection()


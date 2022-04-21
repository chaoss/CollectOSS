Workers
========

**THIS SECTION IS UNDER CONSTRUCTION.**

If you have questions or would like to help please open an issue on GitHub_.

.. _GitHub: https://github.com/chaoss/augur/issues


.. toctree::
   :maxdepth: 1

   creating_a_new_worker
   clustering_worker
   discourse_analysis_worker
   insight_worker
   message_insights_worker
   pull_request_analysis_worker

Gitlab Merge Request Worker
------------------------------------------------

Models & Tables they populate-

1. merge_requests:  This model deals with the data related to Merge Requests(MR) of a project. The tables populated are mentioned below-

    1.1.  pull_requests: The data relating to each MR is stored in this table.

    1.2.  pull_request_labels: Stores Labels of each MR.

    1.3.  pull_request_assignees: Stores the assignees of the MR.

    1.4.  pull_request_reviewers: Stores the list of all possible reviewers for the MR.

    1.5.  pull_request_events: Events like merged, closed, etc for each MR with their timestamp are stored in this table.

    1.6.  pull_request_meta: Stores meta data of the MR, like the info of the base.

    1.7.  pull_request_message_ref: Stores reference data for each message.

    1.8.  pull_request_repo: Stores the data related to the project to which the MR belongs.

    1.9.  message: Stores the messages on the MR thread.

    1.10: contributors: Stores the information related to each contributor of the project. Its implementation is in the base worker class. `query_gitlab_contributors`

2. merge_request_commits:  This model deals with the commit data of each MR-

    2.1. pull_request_commits: Commits and their details are stored in this table along with the MR ID for mapping.

3. merge_request_files: This model deals with the details of changes made in a file.

    3.1. pull_request_files: Stores details of changes made in each file


This worker has an architecture same as the Pull Request Worker. Whenever you send a task for any model, it hits the API
endpoints to fetch the data. Duplicates are ignored and only upsert operations (Update/Insert) are performed.
The tables in which the data is populated are common for both Github Pull Request Worker & Gitlab Merge Request Worker.
The tables and the columns are made with respect to the Github API naming and logic as initially Augur only supported
Github worker. But it is easy to understand the mapping between the naming conventions of Github & Gitlab API.



There are only a few considerable differences between the APIs:

    1. Project can be owned by a group of people in Gitlab while in Github, there is always a unique repo owner (basically the one who created the repo). Repo could be owned by an organization but the Github API values the repo creator and returns the creator as the unique owner.
    Although Gitlab doesn't differentiate between the group of owners and the project creator, we explicitly store
    the Gitlab project creator as the unique owner.

    2.Gitlab API returns the email addresses of closed Gitlab accounts but they don't have a unique source id associated with them. They have a login/username which is enough for our use-case.

    3.Gitlab allows 10X more requests per minute than Github API, so you may not need to store multiple API keys in the worker_oauth table.







Gitlab Issues Worker - Populated Models
------------------------------------------------

1. issues:  This model deals with the data related to the issues of a project. The tables populated are mentioned below-

    1.1.  issues: The data related to each issue(issue name, gitlab issue id, date_created, etc..) is stored in this table.

    1.2.  issue_labels: Stores Labels of each issue.

    1.3.  issues_assignees: Stores the assignees of the issue.

    1.4.  issue_messages: Stores all of the comments associated with a particular issue.

    1.5.  issue_events: Events like opened, closed, etc for each issue are stored in this table.



This worker has an architecture similar to that of the Gitlab Issues Worker. Whenever you send a task for issue collection, it hits the API
endpoints to fetch the data. Duplicates are ignored and only upsert operations (Update/Insert) are performed.
The issues model acts as a central repository for Github & Gitlab issue workers.
Some of the columns present in the tables might be a bit off with respect to the Gitlab Worker, but easily perceptible.

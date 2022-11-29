"""
This file contains functions that take the api response 
and return only the data that the database needs
"""
from augur.tasks.util.AugurUUID import GithubUUID
import sqlalchemy as s

from typing import List


# retrieve only the needed data for pr labels from the api response
def extract_needed_pr_label_data(labels: List[dict], repo_id: int, tool_source: str, tool_version: str, data_source: str) -> List[dict]:

    if len(labels) == 0:
        return []

    label_dicts = []
    for label in labels:

        label_dict = {
            # store the pr_url data on in the pr label data for now so we can relate it back to a pr later
            'pr_src_id': int(label['id']),
            'pr_src_node_id': label['node_id'],
            'pr_src_url': label['url'],
            'pr_src_description': label['name'],
            'pr_src_color': label['color'],
            'pr_src_default_bool': label['default'],
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

        # label_obj = PullRequestLabels(**label_dict)

        label_dicts.append(label_dict)

    return label_dicts

# retrieve only the needed data for pr assignees from the api response
def extract_needed_pr_assignee_data(assignees: List[dict], repo_id: int, tool_source: str, tool_version: str, data_source: str) -> List[dict]:

    if len(assignees) == 0:
        return []


    assignee_dicts = []
    for assignee in assignees:

        assignee_dict = {
            # store the pr_url data on in the pr assignee data for now so we can relate it back to a pr later
            'contrib_id': assignee["cntrb_id"],
            'pr_assignee_src_id': int(assignee['id']),
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

        assignee_dicts.append(assignee_dict)
 
    return assignee_dicts

# retrieve only the needed data for pr reviewers from the api response
def extract_needed_pr_reviewer_data(reviewers: List[dict], repo_id: int, tool_source: str, tool_version: str, data_source: str) -> List[dict]:

    if len(reviewers) == 0:
        return []

    reviewer_dicts = []
    for reviewer in reviewers:

        reviewer_dict = {
            'cntrb_id': reviewer["cntrb_id"],
            'pr_reviewer_src_id': int(float(reviewer['id'])),
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

        reviewer_dicts.append(reviewer_dict)


    return reviewer_dicts

def extract_needed_pr_metadata(metadata_list: List[dict], repo_id: int, tool_source: str, tool_version: str, data_source: str) -> List[dict]:

    if len(metadata_list) == 0:
        return []

    metadata_dicts = []
    for meta in metadata_list:

        metadata_dict = {
            'pr_head_or_base': meta['pr_head_or_base'],
            'pr_src_meta_label': meta['label'],
            'pr_src_meta_ref': meta['ref'],
            'pr_sha': meta['sha'],
            # Cast as int for the `nan` user by SPG on 11/28/2021; removed 12/6/2021
            'cntrb_id': meta["cntrb_id"] if "cntrb_id" in meta else None,
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

        metadata_dicts.append(metadata_dict)

    return metadata_dicts


def extract_pr_review_message_ref_data(comment: dict, pr_review_id, repo_id: int, tool_version: str, data_source: str) -> dict:

    pr_review_comment_message_ref = {
        # msg_id turned up null when I removed the cast to int ..
        'msg_id': comment["msg_id"],
        'pr_review_msg_url': comment['url'],
        'pr_review_src_id': int(pr_review_id),
        'pr_review_msg_src_id': int(comment['id']),
        'pr_review_msg_node_id': comment['node_id'],
        'pr_review_msg_diff_hunk': comment['diff_hunk'],
        'pr_review_msg_path': comment['path'],
        'pr_review_msg_position': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['position']
        ) else comment['position'],
        'pr_review_msg_original_position': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['original_position']
        ) else comment['original_position'],
        'pr_review_msg_commit_id': str(comment['commit_id']),
        'pr_review_msg_original_commit_id': str(comment['original_commit_id']),
        'pr_review_msg_updated_at': comment['updated_at'],
        'pr_review_msg_html_url': comment['html_url'],
        'pr_url': comment['pull_request_url'],
        'pr_review_msg_author_association': comment['author_association'],
        'pr_review_msg_start_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['start_line']
        ) else comment['start_line'],
        'pr_review_msg_original_start_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['original_start_line']
        ) else int(comment['original_start_line']),
        'pr_review_msg_start_side': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            str(comment['start_side'])
        ) else str(comment['start_side']),
        'pr_review_msg_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['line']
        ) else int(comment['line']),
        'pr_review_msg_original_line': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            # 12/6/2021 - removed casting from value check
            comment['original_line']
        ) else int(comment['original_line']),
        'pr_review_msg_side': s.sql.expression.null() if not (  # This had to be changed because "None" is JSON. SQL requires NULL SPG 11/28/2021
            str(comment['side'])
        ) else str(comment['side']),
        'tool_source': 'pull_request_reviews model',
        'tool_version': tool_version + "_reviews",
        'data_source': data_source,
        'repo_id': repo_id
    }

    # pr_comment_msg_ref = {
    #     'pull_request_id': pr_id,
    #     # to cast, or not to cast. That is the question. 12/6/2021
    #     'msg_id': msg_id,
    #     'pr_message_ref_src_comment_id': int(comment['id']),
    #     'pr_message_ref_src_node_id': comment['node_id'],
    #     'tool_source': tool_source,
    #     'tool_version': tool_version,
    #     'data_source': data_source,
    #     'repo_id': repo_id
    # }

    return pr_review_comment_message_ref


def extract_pr_event_data(event: dict, pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> dict:

    # TODO: Add db pull request id

    pr_event = {
        'pull_request_id': pr_id,
        'cntrb_id': event["cntrb_id"] if "cntrb_id" in event else None,
        'action': event['event'],
        'action_commit_hash': None,
        'created_at': event['created_at'],
        'issue_event_src_id': int(event['issue']["id"]),
        'node_id': event['node_id'],
        'node_url': event['url'],
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': data_source,
        'pr_platform_event_id': int(event['issue']["id"]),
        'platform_id': platform_id,
        'repo_id': repo_id
    }

    return pr_event


def extract_issue_event_data(event: dict, issue_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> dict:

    # TODO: Add db pull request id

    issue_event = {
        'issue_event_src_id': int(event['id']),
        'issue_id': issue_id,
        'node_id': event['node_id'],
        'node_url': event['url'],
        'cntrb_id': event["cntrb_id"] if "cntrb_id" in event else None,
        'created_at': event['created_at'] if (
            event['created_at']
        ) else None,
        'action': event['event'],
        'action_commit_hash': event['commit_id'],
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': data_source,
        'repo_id': repo_id,
        'platform_id': platform_id
    }

    return issue_event


def extract_needed_issue_assignee_data(assignees: List[dict], repo_id: int, tool_source: str, tool_version: str, data_source: str) -> List[dict]:

    if len(assignees) == 0:
        return []


    assignee_dicts = []
    for assignee in assignees:

        assignee_dict = {
            'cntrb_id': assignee["cntrb_id"], # # this is added to the data by the function process_issue_contributors in issue_tasks.py
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'issue_assignee_src_id': int(assignee['id']),
            'issue_assignee_src_node': assignee['node_id'],
            'repo_id': repo_id 
        }

        assignee_dicts.append(assignee_dict)

    return assignee_dicts



# retrieve only the needed data for pr labels from the api response
def extract_needed_issue_label_data(labels: List[dict], repo_id: int, tool_source: str, tool_version: str, data_source: str) -> List[dict]:

    if len(labels) == 0:
        return []

    label_dicts = []
    for label in labels:

        label_dict = {
            'label_text': label['name'],
            'label_description': label['description'] if 'description' in label else None,
            'label_color': label['color'],
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'label_src_id': int(label['id']),
            'label_src_node_id': label['node_id'],
            'repo_id': repo_id 
        }

        # label_obj = PullRequestLabels(**label_dict)

        label_dicts.append(label_dict)

    return label_dicts



# retrieve only the needed data for pr labels from the api response
def extract_needed_issue_message_ref_data(message: dict, issue_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> List[dict]:

    message_ref_dict = {
        'issue_id': issue_id,
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': data_source,
        'issue_msg_ref_src_comment_id': int(message['id']),
        'issue_msg_ref_src_node_id': message['node_id'],
        'repo_id': repo_id
    }

    return message_ref_dict

# retrieve only the needed data for pr labels from the api response
def extract_needed_pr_message_ref_data(comment: dict, pull_request_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> List[dict]:

    message_ref_dict = {
            'pull_request_id': pull_request_id,
            'pr_message_ref_src_comment_id': int(comment['id']),
            'pr_message_ref_src_node_id': comment['node_id'],
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
    }
                

    return message_ref_dict
     

def extract_needed_pr_data(pr, repo_id, tool_source, tool_version):
    

    pr_dict = {
        'repo_id': repo_id,
        'pr_url': pr['url'],
        # 1-22-2022 inconsistent casting; sometimes int, sometimes float in bulk_insert
        'pr_src_id': int(str(pr['id']).encode(encoding='UTF-8').decode(encoding='UTF-8')),
        # 9/20/2021 - This was null. No idea why.
        'pr_src_node_id': pr['node_id'],
        'pr_html_url': pr['html_url'],
        'pr_diff_url': pr['diff_url'],
        'pr_patch_url': pr['patch_url'],
        'pr_issue_url': pr['issue_url'],
        'pr_augur_issue_id': None,
        'pr_src_number': pr['number'],
        'pr_src_state': pr['state'],
        'pr_src_locked': pr['locked'],
        'pr_src_title': str(pr['title']),
        'pr_augur_contributor_id': pr["cntrb_id"],
        ### Changed to int cast based on error 12/3/2021 SPG (int cast above is first change on 12/3)
        'pr_body': str(pr['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
            pr['body']
        ) else None,
        'pr_created_at': pr['created_at'],
        'pr_updated_at': pr['updated_at'],
        'pr_closed_at': None if not (
            pr['closed_at']
        ) else pr['closed_at'],
        'pr_merged_at': None if not (
            pr['merged_at']
        ) else pr['merged_at'],
        'pr_merge_commit_sha': pr['merge_commit_sha'],
        'pr_teams': None,
        'pr_milestone': None,
        'pr_commits_url': pr['commits_url'],
        'pr_review_comments_url': pr['review_comments_url'],
        'pr_review_comment_url': pr['review_comment_url'],
        'pr_comments_url': pr['comments_url'],
        'pr_statuses_url': pr['statuses_url'],
        'pr_meta_head_id': None if not (
            pr['head']
        ) else pr['head']['label'],
        'pr_meta_base_id': None if not (
            pr['base']
        ) else pr['base']['label'],
        'pr_src_issue_url': pr['issue_url'],
        'pr_src_comments_url': pr['comments_url'],
        'pr_src_review_comments_url': pr['review_comments_url'],
        'pr_src_commits_url': pr['commits_url'],
        'pr_src_statuses_url': pr['statuses_url'],
        'pr_src_author_association': pr['author_association'],
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': 'GitHub API'
    }

    return pr_dict

def extract_needed_issue_data(issue: dict, repo_id: int, tool_source: str, tool_version: str, data_source: str):

    dict_data = {
        'cntrb_id': None, # this the contributor who closed the issue
        'repo_id': repo_id,
        'reporter_id': issue["cntrb_id"], # this is the contributor who opened the issue
        'pull_request': None,
        'pull_request_id': None,
        'created_at': issue['created_at'],
        'issue_title': str(issue['title']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
            issue['title']
        ) else None,
        # 'issue_body': issue['body'].replace('0x00', '____') if issue['body'] else None,
        'issue_body': str(issue['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
            issue['body']
        ) else None,
        'comment_count': issue['comments'],
        'updated_at': issue['updated_at'],
        'closed_at': issue['closed_at'],
        'repository_url': issue['repository_url'],
        'issue_url': issue['url'],
        'labels_url': issue['labels_url'],
        'comments_url': issue['comments_url'],
        'events_url': issue['events_url'],
        'html_url': issue['html_url'],
        'issue_state': issue['state'],
        'issue_node_id': issue['node_id'],
        'gh_issue_id': issue['id'],
        'gh_issue_number': issue['number'],
        'gh_user_id': issue['user']['id'],
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': data_source
        }

    return dict_data

def extract_needed_message_data(comment: dict, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str):

    dict_data = {
        'pltfrm_id': platform_id,
        'msg_text': str(comment['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
            comment['body']
        ) else None,
        'msg_timestamp': comment['created_at'],
        'cntrb_id': comment["cntrb_id"],
        'tool_source': tool_source,
        'tool_version': tool_version,
        'data_source': data_source,
        'repo_id': repo_id,
        'platform_msg_id': int(comment['id']),
        'platform_node_id': comment['node_id']
    }

    return dict_data

def extract_need_pr_review_data(reviews, platform_id, repo_id, tool_version, data_source):

    if len(reviews) == 0:
        return []

    review_data = []
    for review in reviews:

        pr_review_dict = {
                'cntrb_id': None,
                'pr_review_author_association': review['author_association'],
                'pr_review_state': review['state'],
                'pr_review_body': str(review['body']).encode(encoding='UTF-8',errors='backslashreplace').decode(encoding='UTF-8',errors='ignore') if (
                    review['body']
                ) else None,
                'pr_review_submitted_at': review['submitted_at'] if (
                    'submitted_at' in review
                ) else None,
                'pr_review_src_id': int(float(review['id'])), #12/3/2021 cast as int due to error. # Here, `pr_review_src_id` is mapped to `id` SPG 11/29/2021. This is fine. Its the review id.
                'pr_review_node_id': review['node_id'],
                'pr_review_html_url': review['html_url'],
                'pr_review_pull_request_url': review['pull_request_url'],
                'pr_review_commit_id': review['commit_id'],
                'tool_source': 'pull_request_reviews model',
                'tool_version': tool_version+ "_reviews",
                'data_source': data_source,
                'repo_id': repo_id,
                'platform_id': platform_id 
        }

        review_data.append(pr_review_dict)

    return review_data

def extract_needed_contributor_data(contributor, tool_source, tool_version, data_source):

    cntrb_id = GithubUUID()   
    cntrb_id["user"] = contributor["id"]

    contributor = {
            "cntrb_id": cntrb_id.to_UUID(),
            "cntrb_login": contributor['login'],
            "cntrb_created_at": contributor['created_at'] if 'created_at' in contributor else None,
            "cntrb_email": contributor['email'] if 'email' in contributor else None,
            "cntrb_company": contributor['company'] if 'company' in contributor else None,
            "cntrb_location": contributor['location'] if 'location' in contributor else None,
            # "cntrb_type": , dont have a use for this as of now ... let it default to null
            "cntrb_canonical": contributor['email'] if 'email' in contributor else None,
            "gh_user_id": contributor['id'],
            "gh_login": str(contributor['login']),  ## cast as string by SPG on 11/28/2021 due to `nan` user
            "gh_url": contributor['url'],
            "gh_html_url": contributor['html_url'],
            "gh_node_id": contributor['node_id'],
            "gh_avatar_url": contributor['avatar_url'],
            "gh_gravatar_id": contributor['gravatar_id'],
            "gh_followers_url": contributor['followers_url'],
            "gh_following_url": contributor['following_url'],
            "gh_gists_url": contributor['gists_url'],
            "gh_starred_url": contributor['starred_url'],
            "gh_subscriptions_url": contributor['subscriptions_url'],
            "gh_organizations_url": contributor['organizations_url'],
            "gh_repos_url": contributor['repos_url'],
            "gh_events_url": contributor['events_url'],
            "gh_received_events_url": contributor['received_events_url'],
            "gh_type": contributor['type'],
            "gh_site_admin": contributor['site_admin'],
            "cntrb_last_used" : None if 'updated_at' not in contributor else contributor['updated_at'],
            "cntrb_full_name" : None if 'name' not in contributor else contributor['name'],
            "tool_source": tool_source,
            "tool_version": tool_version,
            "data_source": data_source
        }

    return contributor





                




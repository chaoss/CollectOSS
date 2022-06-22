
"""
This file contains functions that take the api response 
and return only the data that the database needs
"""



# retrieve only the needed data for pr labels from the api response
def extract_needed_pr_label_data(labels: [dict], pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> [dict]:

    if len(labels) == 0:
        return []

    label_dicts = []
    for label in labels:

        label_dict = {
            'pull_request_id': pr_id,
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
def extract_needed_pr_assignee_data(assignees: [dict], pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> [dict]:

    if len(assignees) == 0:
        return []


    assignee_dicts = []
    for assignee in assignees:

        assignee_dict = {
            'pull_request_id': pr_id,
            'contrib_id': None,
            'pr_assignee_src_id': int(assignee['id']),
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

        assignee_dicts.append(assignee_dict)

    return assignee_dicts

# retrieve only the needed data for pr reviewers from the api response
def extract_needed_pr_reviewer_data(reviewers: [dict], pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> [dict]:

    if len(reviewers) == 0:
        return []

    reviewer_dicts = []
    for reviewer in reviewers:

        reviewer_dict = {
            'pull_request_id': pr_id,
            'cntrb_id': None,
            'pr_reviewer_src_id': int(float(reviewer['id'])),
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

    reviewer_dicts.append(reviewer_dict)

    return reviewer_dicts


def extract_needed_pr_metadata(metadata_list: [dict], pr_id: int, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> [dict]:

    if len(metadata_list) == 0:
        return []

    metadata_dicts = []
    for meta in metadata_list:

        metadata_dict = {
            'pull_request_id': pr_id,
            'pr_head_or_base': meta['pr_head_or_base'],
            'pr_src_meta_label': meta['label'],
            'pr_src_meta_ref': meta['ref'],
            'pr_sha': meta['sha'],
            # Cast as int for the `nan` user by SPG on 11/28/2021; removed 12/6/2021
            'cntrb_id': None,
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id
        }

        metadata_dicts.append(metadata_dict)

    return metadata_dicts



def extract_pr_comment_ref_data(comment: dict, pr_id: int, msg_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str) -> dict:

    pr_review_comment_message_ref = {
        'pr_review_id':  pr_id,
        # msg_id turned up null when I removed the cast to int ..
        'msg_id': msg_id,
        'pr_review_msg_url': comment['url'],
        'pr_review_src_id': int(comment['pull_request_review_id']),
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
        'cntrb_id': None,
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
        'cntrb_id': None,
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

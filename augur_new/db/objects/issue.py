from augur_new.objects.github import GithubObject

class IssueObject(GithubObject):
    def __init__(self, issue: dict, repo_id: int, tool_source: str, tool_version: str, data_source: str):

        dict_data = {
            'repo_id': repo_id,
            'reporter_id': None,
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

        super().__init__(dict_data)
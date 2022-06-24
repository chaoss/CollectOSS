from augur_new.db.objects.github import GithubObject

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

        source_assignees = []

        # loops through the list of assignees that github returns
        for assignee in issue['assignees']:

            if assignee:

                if not is_nan(issue['assignee']):

                    source_assignees.append(assignee)

        before_assignee_ids = [assignee["id"] for assignee in source_assignees]

        # handles the asignee field that github returns
        issue_assignee = issue['assignee']

        if issue_assignee:

            if issue_assignee not in source_assignees:

                print(f"Please tell Andrew is this occurs! ASSIGNEE not in Assignees list. Issue_id: {gh_issue_id}. Assignee data: {issue_assignee}")

                if not is_nan(issue_assignee):

                    source_assignees.append(issue_assignee)

        after_assignee_ids = [assignee["id"] for assignee in source_assignees]
              

        self.assignees = source_assignees
        self.labels = issue["labels"]

        assignee_ids = [assignee["id"] for assignee in self.assignees]

        if checkIfDuplicates_1(assignee_ids):

            print(f"DUPLICATE assignees: {assignee_ids}")
            print(f"Before assignee ids: {before_assignee_ids}")
            print(f"After assignee ids: {after_assignee_ids}")
            print(f"Data assignees: {issue['assignees']}")
            print(f"Data assignee: {issue_assignee}")


        super().__init__(dict_data)

def is_nan(value):

    it_is_nan = type(value) == float and math.isnan(value)

    if it_is_nan:
        print(f"Please tell Andrew is this occurs! Nan assignee: {value}")

    return it_is_nan

def checkIfDuplicates_1(listOfElems):
    ''' Check if given list contains any duplicates '''
    if len(listOfElems) == len(set(listOfElems)):
        return False
    else:
        return True
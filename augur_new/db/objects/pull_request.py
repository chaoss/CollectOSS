from augur_new.db.objects.github import GithubObject

class PrObject():
    def __init__(self, pr, repo_id, tool_source, tool_version):

        self.data = {
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
            'pr_augur_contributor_id': None,
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

        self.db_row = None

        self.labels = pr["labels"]
        self.assignees = pr["assignees"]
        self.metadata = [pr["head"], pr["base"]]

    def set_db_row(self, row):
        self.db_row = row

    def get_dict(self):
        return self.data



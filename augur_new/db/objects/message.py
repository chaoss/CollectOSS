from augur_new.objects.github import GithubObject

class PrCommentObject(GithubObject):
    def __init__(self, comment: dict, platform_id: int, repo_id: int, tool_source: str, tool_version: str, data_source: str):

        dict_data = {
            'pltfrm_id': platform_id,
            'msg_text': str(comment['body']).encode(encoding='UTF-8', errors='backslashreplace').decode(encoding='UTF-8', errors='ignore') if (
                comment['body']
            ) else None,
            'msg_timestamp': comment['created_at'],
            'cntrb_id': None,
            'tool_source': tool_source,
            'tool_version': tool_version,
            'data_source': data_source,
            'repo_id': repo_id,
            'platform_msg_id': int(comment['id']),
            'platform_node_id': comment['node_id']
        }

        super().__init__(dict_data)
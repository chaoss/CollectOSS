


class GithubObject():

    def __init__(self, data: dict):

        self.data = data
        self.db_row = None

    def set_db_row(self, row):
        self.db_row = row

    def get_dict(self) -> dict:
        return self.data

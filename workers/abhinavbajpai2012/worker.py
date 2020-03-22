import gitlab
import os
import json as json_lib
from utils import flatten_json, RowDataSetter
from constants import GITLAB_ADDRESS, OUTPUT_PATH


class GitlabWorker(object):

    def __init__(self, token):

        self.gl_client = gitlab.Gitlab(GITLAB_ADDRESS, private_token=token)
        self.gl_client.auth()
        self.setter_client = RowDataSetter()

    def get_all_owned_projects(self):
        """
        Retrieves all the owned projects of the user
        :return: list: list of all projects owned by the API_KEY generator's ID
        """
        projects = self.gl_client.projects.list(owned=True, all=True)
        return projects

    @staticmethod
    def get_project_issues(project):
        """
        Retrieves all issues related to the project
        :param project: project class object: project of which issues need to be extracted
        :return: list: list of issues as list of dict
        """
        issues = project.issues.list()
        issue_json_list = [flatten_json(issue.__dict__['_attrs']) for issue in issues]
        return issue_json_list

    @staticmethod
    def get_project_branches(project):
        """
        Retrieves all branches related to the project specified
        :param project: project class object: project of which branches need to be extracted
        :return: list: list of branches as list of dict
        """
        branches = project.branches.list()
        branch_json_list = [flatten_json(branch.__dict__['_attrs']) for branch in branches]
        return branch_json_list

    @staticmethod
    def get_project_commits(project):
        """
        Retrieves all commits related to the project specified
        :param project: project class object: project of which commits need to be extracted
        :return: list of commits as list of dict
        """
        commits = project.commits.list()
        commit_json_list = [flatten_json(commit.__dict__['_attrs']) for commit in commits]
        return commit_json_list

    @staticmethod
    def get_project_merge_requests(project):
        """
        Retrieves all merge requests related to the project specified
        :param project: project class object: project of which commits need to be extracted
        :return: list of merge requests as a list of dictionary
        """
        merge_requests = project.mergerequests.list()
        merge_request_json_list = [flatten_json(mr.__dict__['_attrs']) for mr in merge_requests]
        return merge_request_json_list

    @staticmethod
    def make_directory(dir_path):
        """
        A function which makes directory after checking it's presence
        :param dir_path: path of the directory
        :return:
        """
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)

    def make_directories_for_project(self, dir_name):
        """
        Makes directories to store project details
        :param dir_name: str: name of directory
        :return:
        """
        self.make_directory(dir_name)
        self.make_directory(dir_name + "/Issues")
        self.make_directory(dir_name + "/Branches")
        self.make_directory(dir_name + "/Commits")
        self.make_directory(dir_name + "/Merge_Requests")

    @staticmethod
    def get_name_from_json(json):
        """

        extracts unique id/name to store the json file
        :param json: dict
        :return: str: unique id/name
        """
        name = json.get(u'name', None)
        if name is None:
            name = json.get(u'iid', None)
        if name is None:
            name = json.get(u'id', None)
        if name is None:
            name = json.get(u'title', None)
        return str(name).replace('/', '_or_')

    def save_json_list(self, dir_path, json_list):
        """

        This function stores the JSONs at the path specified
        :param dir_path: str: path to the directory
        :param json_list: list: list of JSONs to be stored
        :return:
        """
        for json in json_list:
            json_path = dir_path + '/' + self.get_name_from_json(json) + '.json'
            with open(json_path, 'w') as fp:
                json_lib.dump(json, fp)
    
    def save_in_directory(self, dir_name, project_json, issue_json_list, branch_json_list, commit_json_list,
                          merge_request_json_list):
        """

        saves Project data in the path specified
        :param dir_name: str: name/path of directory in which data needs to be saved
        :param project_json: dict: contains project detail
        :param issue_json_list: list: list of issues of the project
        :param branch_json_list: list: list of branches of the project
        :param commit_json_list: list: list of commits of the project
        :param merge_request_json_list: list: list of merge requests of the project
        :return:
        """
        self.make_directories_for_project(dir_name)
        self.save_json_list(dir_name, [project_json])
        self.save_json_list(dir_name + "/Issues", issue_json_list)
        self.save_json_list(dir_name + "/Branches", branch_json_list)
        self.save_json_list(dir_name + "/Commits", commit_json_list)
        self.save_json_list(dir_name + "/Merge_Requests", merge_request_json_list)

    def store_owned_project_data(self):
        """

        Stores branches, commits, issues and merge requests of all the projects owned by the user.
        :return:
        """
        projects = self.get_all_owned_projects()
        self.make_directory(OUTPUT_PATH)
        for project in projects:
            project_json = flatten_json(project.__dict__['_attrs'])
            dir_name = OUTPUT_PATH + "/project_" + self.setter_client.put_string(project_json[u'name'])
            issue_json_list = self.get_project_issues(project)
            branch_json_list = self.get_project_branches(project)
            commit_json_list = self.get_project_commits(project)
            merge_request_json_list = self.get_project_merge_requests(project)
            self.save_in_directory(dir_name, project_json, issue_json_list, branch_json_list, commit_json_list,
                                   merge_request_json_list)


def main():

    gl_worker = GitlabWorker('API_KEY')
    gl_worker.store_owned_project_data()


if __name__ == "__main__":

    main()

from pygit2 import Repository, GitError


class GitRepo:
    @classmethod
    def clone(cls, repo_url:str, under:str, name:str, timeout=7200):
        """Clone a git repo into a folder under a particular directory with a given name

        Args:
            repo_url (str): The repository URL to clone to
            into (str): the folder under/inside which to perform the clone (working dir)
            name (str): the name of the folder the repo should be stored in
            timeout (int): how many seconds to wait before cancelling the operation
        """
        pass

    @classmethod
    def pull(cls, git_dir:str, timeout=600):
        """Pull updates from an already-cloned git repo

        Args:
            git_dir (str): The repository directory to perform the pull in (working dir/repo dir)
        """
        pass

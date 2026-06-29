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
            timeout (int): how many seconds to wait before cancelling the operation
        """
        pass

    @classmethod
    def checkout(cls, git_dir:str, branch:str, timeout=600):
        """Checkout a given branch in an already-cloned git repo

        Args:
            git_dir (str): The repository directory to perform the checkout in (working dir/repo dir)
            branch (str): The branch to checkout
            timeout (int): how many seconds to wait before cancelling the operation
        """
        pass

    @classmethod
    def get_default_remote(cls, git_dir:str, timeout=600) -> str:
        """Get the default remote for an already-cloned git repo

        Args:
            git_dir (str): The repository directory to perform the get default remote in (working dir/repo dir)
            timeout (int): how many seconds to wait before cancelling the operation
        """
        pass

    @classmethod
    def get_remote_default_branch(cls, git_dir:str, remote_name:str, timeout=600) -> str:
        """Get the default remote branch for an already-cloned git repo

        Args:
            git_dir (str): The repository directory to perform the get remote default branch in (working dir/repo dir)
            remote_name (str): The name of the remote to get the default branch for
            timeout (int): how many seconds to wait before cancelling the operation
        """
        # get remote default branch : "git -C {absolute_path} remote show origin | sed -n '/HEAD branch/s/.*: //p'")
        pass

    @classmethod
    def commit_message(cls, git_dir:str, commit_hash:str, timeout=600) -> str:
        """return the commit message for a given commit hash

        Args:
            git_dir (str): The repository directory to perform the pull in (working dir/repo dir)
            commit_hash (str): The hash of the commit to fetch
            timeout (int): how many seconds to wait before cancelling the operation
        """
        pass

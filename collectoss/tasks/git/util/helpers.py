from pathlib import Path

from collectoss.application.db.lib import get_clone_path_by_repo_id, get_repo_by_repo_id, set_clone_path_by_repo_id

def is_git_repo(path:Path) -> bool:
    if not path.exists():
        return False
    
    gitdir = path.joinpath(".git")
    if not gitdir.exists():
        return False
    return True

def get_absolute_clone_path(facade_base_directory: str | Path, repo_id: int) -> Path:
    """Returns the absolute path to the clone of the repo on disk

    This method tries several methods to get the clone path and will automatically 
    update the database with the correct path if a less-than-ideal method is used.

    This method expects that the clone directory already exists.
    See `git_repo_initialize` for the method that creates the clone directory.

    Args:
        facade_base_directory (str): the configured base directory that all facade clones paths are relative to
        repo_id (int): the id of the repo to get the clone path for
    """

    base_dir = Path(facade_base_directory)

    # check if [configured facade base dir] + [path from db operations table] exists and is a git repo (happy path/ideal case)
    clone_path = get_clone_path_by_repo_id(repo_id)
    if clone_path and is_git_repo(base_dir.joinpath(clone_path)):
        return base_dir.joinpath(clone_path)
    # if not, use the current path building technique ( [configured facade base dir] + [path from db data table] + [repo name]). if success, rewrite the facade path and return it
    repo = get_repo_by_repo_id(repo_id)
    
    # absolute_path = get_absolute_repo_path(base_dir, repo.repo_id, repo.repo_path,repo.repo_name)
    legacy_path = f"{repo_id}-{repo.repo_path}/{repo.repo_name}"
    if legacy_path and is_git_repo(base_dir.joinpath(legacy_path)):
        set_clone_path_by_repo_id(repo_id, legacy_path)
        return base_dir.joinpath(legacy_path)

    # if not, discover it (check just the facade path from step 1, if it contains just one dir, use that and update the database else fail)
    discover_path = base_dir.joinpath(f"{repo_id}-{repo.repo_path}")
    discovered_directories = []
    if discover_path.exists():
        discovered_directories = [x for x in discover_path.iterdir() if x.is_dir()]
        if len(discovered_directories) == 1 and is_git_repo(discover_path.joinpath(discovered_directories[0])):
            discovered_repo = discovered_directories[0]  # already an absolute Path
            set_clone_path_by_repo_id(repo_id, str(discovered_repo.relative_to(base_dir)))
            return discovered_repo


    raise ValueError(f"""No valid git repo path found for repo {repo_id} ({repo.repo_git}).
    Attempted paths:
    - {base_dir.joinpath(clone_path) if clone_path else '(not set)'}
    - {base_dir.joinpath(legacy_path)}
    - {discover_path} ({len(discovered_directories)} children)
    """)

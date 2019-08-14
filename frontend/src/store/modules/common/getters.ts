export default {
  repoRelations: (state: any) => {
    let repoRelations:any = {}, repos = state.cache.getRepos || [], repoGroups = state.cache.getRepoGroups || []
    repoGroups.forEach((group: any) => {
      // Move down between future relation endpoint
      repoRelations[group.rg_name] = {};
      repos.filter((repo: any) => {
        return repo.rg_name === group.rg_name;
      }).forEach((repo: any) => {
        repoRelations[group.rg_name][repo.url] = repo
      });
    });
    return repoRelations;
  },
  repoGroups: (state:any) => {
    return state.cache.getRepoGroups || [];
  },
  repos: (state: any) => {
    return state.cache.getRepos || []
  },
  apiGroups: (state: any) => {
    return state.apiGroups;
  },
  apiRepos: (state: any) => {
    return state.apiRepos;
  },
  cache: (state:any) => (repo: string, endpoint: string) =>{
    return state.cache[repo][endpoint];
  },
  AugurAPI: (state: any) => {
    return state.AugurAPI;
  },
  gitRepo: (state: any) => {
      return state.gitRepo;
  },
  repo_groups: (state: any) => {
    return state.cache.getRepoGroups
  },
  sorted_repos: (state:any) => (col: string, ascending: boolean) => {
      if (state.cache.getRepos == undefined) {
          return []
      }
      const items = [...state.cache.getRepos].sort((a,b) => {
      if (a[col] > b[col]) {
        return ascending ? 1 : -1
      } else if (a[col] < b[col]) {
        return ascending ? -1 : 1
      }
      return 0;
    })
    return items
  },
  sorted_repo_groups: (state:any) => (col:string, ascending: boolean) => {
    const items = [...state.cache.getRepoGroups].sort((a,b) => {
      if (a[col] > b[col]) {
        return ascending ? 1 : -1
      } else if (a[col] < b[col]) {
        return ascending ? -1 : 1
      }
      return 0;
    })
    return items
  },
  loaded_repos: (state:any) => {
      return state.cache.getRepos != null;
  },
  loaded_groups: (state:any) => {
      return state.cache.getRepoGroups != null;
  },
};

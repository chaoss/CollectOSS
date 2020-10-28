// #SPDX-License-Identifier: MIT
export default {
  repoRelations: (state: any) => {
    let repoRelations:any = {}, repos = state.cache.getRepos || [], repoGroups = state.cache.getRepoGroups || []
    repoGroups.forEach((group: any) => {
      // Move down between future relation endpoint
      repoRelations[group.rg_name] = {};
      repos.filter((repo: any) => {
        return repo.rg_name === group.rg_name;
      }).forEach((repo: any) => {
        repoRelations[group.rg_name][repo.repo_name] = repo
      });
    });
    return repoRelations;
  },
  repoGroups: (state:any) => {
    return state.cache.getRepoGroups || []
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
  tab: (state: any) => {
    return state.tab
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
  sortedRepos: (state:any) => (col: string, ascending: boolean) => {
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
  sortedReposInGroup: (state:any) => (group:any, col: string, ascending: boolean) => {
    if (state.cache.getRepos == undefined) {
        return []
    }
    let careAbout:any[] = []
    let i:number = 0
    console.log(group, state.cache.getRepos, state.cache.getRepos[0].rg_name, state.cache.getRepos[0].rg_name == group.rg_name)
    for (i = 0; i < state.cache.getRepos.length; i++) {
      if (state.cache.getRepos[i].rg_name == group.rg_name)
        careAbout.push(state.cache.getRepos[i])
    }
    console.log(careAbout)
    const items = careAbout.sort((a:any,b:any) => {
      if (a[col] > b[col]) {
        return ascending ? 1 : -1
      } else if (a[col] < b[col]) {
        return ascending ? -1 : 1
      }
      return 0;
    })
    console.log(items)
    return items
  },
  sortedRepoGroups: (state:any) => (col:string, ascending: boolean) => {
    console.log(state.cache)
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
  loadedRepos: (state:any) => {
      return state.cache.getRepos != null;
  },
  loadedGroups: (state:any) => {
      return state.cache.getRepoGroups != null;
  },
  trailingAverage: (state:any) => {
    return state.trailingAverage
  },
  showDetail: (state:any) => {
    return state.showDetail
  },
  showTooltip: (state:any) => {
    return state.showTooltip
  }
};

export default {
    repoRelationsInfo: (state: any) => {
      return state.repoRelationsInfo;
    },
    groupsInfo: (state: any) => {
      return state.groupsInfo;
    },
    groupsList: (state: any) => {
      return Object.keys(state.groupsInfo);
    },
    AugurAPI: (state: any) => {
      return state.AugurAPI;
    },
    repo: (state: any) => {
        return state.baseRepo
    },
    gitRepo: (state: any) => {
        return state.gitRepo
    },
    repos: (state: any) => {
        // console.log('CHECKED')
        let repos: any[] = []
        Object.keys(state.repoRelationsInfo).forEach((key: any) => {
            Object.keys(state.repoRelationsInfo[key]).forEach((repo_name: any) => {
                repos.push(state.repoRelationsInfo[key][repo_name])
            })
        })
        return repos
    }

};

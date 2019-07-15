export default {
    async getRepoRelations(context: any, payload: object) {
        // console.log(context.state);
        // try {
        //     console.log('INSIDE ACTION:', context.state);
        //     const repoRelationsInfo = context.state.repoRelationsInfo;
        //     const groupsInfo = context.state['groupsInfo'];
        //     context.state.AugurAPI.getRepos().then((data: object[]) => {
        //         let repos = data;
        //         context.state.AugurAPI.getRepoGroups().then((data: object[]) => {
        //             let repo_groups = data;
        //             //move down between future relation endpoint
        //             repo_groups.forEach((group: object): void => {
        //                 repos.filter(function(repo: object) {
        //                     return repo.rg_name == group.rg_name;
        //                 }).forEach((repo: object) => {
        //                     repoRelationsInfo[group.rg_name][repo.url] = ...
        //                          context.state.AugurAPI.Repo({gitURL: repo.url})
        //                 })
        //                 // THIS LINE WILL CHANGE WHEN WE IMPLEMENT A GROUP OBJECT OR CLASS
        //                 // groupsInfo[group] = state.AugurAPI.Repo({gitURL: repo.url})
        //             })
        //         })
        //     })
        //     commit('mutate', {
        //         property: 'repoRelationsInfo',
        //         with: repoRelationsInfo
        //     });
        //     commit('mutate', {
        //         property: 'groupsInfo',
        //         with: groupsInfo
        //     });
        //     return { repoRelationsInfo, groupsInfo };
        // } catch (error) {
        //     throw error;
        // }
    },
    async endpoint(context: any, payload: any) {
        try {
            let tempCache = context.state.cache;
            if ('endpoints' in payload) {
                if ('repos' in payload) {
                    context.state.AugurAPI.batchMapped(payload.repos, payload.endpoints).then(
                        (data: object[]) => {
                            tempCache = {...tempCache, ...data};
                            payload.repos.forEach((repo: any) => {
                                tempCache[repo.url] = {...tempCache[repo.url], ...data[repo.url]};
                            });
                        });
                } else if ('repoGroups' in payload) {
                    context.state.AugurAPI.batchMapped(payload.repoGroups, payload.endpoints).then(
                        (data: object[]) => {
                            tempCache = {...tempCache, ...data};
                            payload.repoGroups.forEach((group: any) => {
                                tempCache[group.rg_name] = {...tempCache[group.rg_name],
                                    ...data[group.rg_name]};
                            });
                        });
                } else {
                    payload.endpoints.forEach((endpoint: string) => {
                        context.state.AugurAPI[endpoint].then((data: object[]) => {
                            tempCache[endpoint] = data;
                        });
                    });
                }
            }
            context.commit('mutate', {
                property: 'cache',
                with: tempCache,
            });
            return tempCache;
        } catch (error) {
            throw error;
        }
    },
};

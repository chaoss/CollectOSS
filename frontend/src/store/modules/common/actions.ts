export default {
    async getRepoRelations(context: any) {
        console.log(context.state);
        try {
            console.log('INSIDE ACTION:', context.state);
            const repoRelationsInfo = context.state.repoRelationsInfo;
            const groupsInfo = context.state['groupsInfo'];
            context.state.AugurAPI.getRepos().then((data: object[]) => {
                let repos = data;
                console.log('checked',repos)
                context.state.AugurAPI.getRepoGroups().then((data: object[]) => {
                    let repo_groups = data;
                    console.log('checked', repo_groups)
                    //move down between future relation endpoint
                    repo_groups.forEach((group: any): void => {
                        repoRelationsInfo[group.rg_name] = {}
                        // THIS LINE WILL CHANGE WHEN WE IMPLEMENT A GROUP OBJECT OR CLASS
                        // groupsInfo[group.rg_name] = context.state.AugurAPI.RepoGroup({rg_name: group.rg_name, repo_group_id: group.repo_group_id})
                        groupsInfo[group.rg_name] = group
                        repos.filter(function(repo: any) {
                            return repo.rg_name == group.rg_name;
                        }).forEach((repo: any) => {
                            repoRelationsInfo[group.rg_name][repo.url] = repo
                            //repoRelationsInfo[group.rg_name][repo.url] = context.state.AugurAPI.Repo({gitURL: repo.url, repo_group_id: group.repo_group_id, repo_id: repo.repo_id})
                        });
                    })
                    context.commit('mutate', {
                        property: 'groupsInfo',
                        with: groupsInfo
                    });
                    context.commit('mutate', {
                        property: ' ',
                        with: repoRelationsInfo
                    });
                })
            });
            console.log(context.state);
            return { repoRelationsInfo, groupsInfo };
        } catch (error) {
            throw error;
        }
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

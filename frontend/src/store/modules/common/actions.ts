import Repo from '@/AugurAPI';
import RepoGroup from '@/AugurAPI';
export default {
    getRepoRelations(context: any, payload: object) {
        return new Promise ((resolve, reject) => {
            setTimeout(() => {
                let repoRelations = context.state.cache.repoRelations || {};
                let repoGroups = context.state.cache.repoGroups || {};
                context.state.AugurAPI.getRepos().then((repos: object[]) => {
                    context.state.AugurAPI.getRepoGroups().then((groups: object[]) => {
                        // Move down between future relation endpoint
                        groups.forEach((group: any): void => {
                            repoGroups[group.rg_name] = group
                            repoRelations[group.rg_name] = {};
                            repos.filter((repo: any) => {
                                return repo.rg_name === group.rg_name;
                            }).forEach((repo: any) => {
                                repoRelations[group.rg_name][repo.url] = repo
                            });
                        });
                        console.log(repoRelations)
                        context.commit('mutateCache', {
                            property: 'repoRelations',
                            with: repoRelations,
                        });
                        context.commit('mutateCache', {
                            property: 'repoGroups',
                            with: repoGroups,
                        });
                    });
                resolve({ repoRelations, repoGroups });
                });
            }, 2000)
        })
    },
    async createAPIObjects(context: any, payload: any) {
        try {
            let groupsInfo = context.state.cache.groupsInfo || {};
            let repoRelationsInfo = context.state.repoRelationsInfo || {};
            if ('repos' in payload) {
                payload.repos.forEach((repo: any) => {
                    console.log(repo)
                    let APIRepo = context.state.AugurAPI.Repo(repo)
                })
            }
            if ('groups' in payload) {
                payload.groups.forEach((group: any) => {
                    console.log(group)
                    let APIRepo = context.state.AugurAPI.RepoGroup(group)
                })
            }
            context.commit('mutate', {
                property: 'repoRelationsInfo',
                with: repoRelationsInfo,
            });
            context.commit('mutate', {
                property: 'groupsInfo',
                with: groupsInfo,
            });
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
    async getRepos(context:any, payload:any){
        try {
            context.state.AugurAPI.getRepos().then((repos: object[]) => {
                context.commit('mutateCache', {
                    property: 'getRepos',
                    with: repos,
                });
            });
        } catch(error) {
            throw error;
        }
    },
    async getRepoGroups(context:any, payload:any){
        try {
            context.state.AugurAPI.getRepoGroups().then((rgs: object[]) => {
                context.commit('mutateCache', {
                    property: 'getRepoGroups',
                    with: rgs,
                });
            });
        } catch(error) {
            throw error;
        }
    },
    async addRepo(context:any, payload:any) {
         return new Promise((resolve, reject) => {
             setTimeout(()=>{
                let rg_name = payload.rg_name || undefined
                let repo_id = payload.repo_id || undefined
                let repo_group_id = payload.repo_group_id || undefined
                let gitURL = payload.url || undefined
                let repo:Repo = context.state.AugurAPI.Repo({gitURL:gitURL,repo_id:repo_id,repo_group_id:repo_group_id})
                
                context.commit('mutateRepoRelation', {repo:repo, url: gitURL,rg_name:rg_name})
                resolve(repo)
             },2000)
         })
    },
    async addRepoGroup(context:any, payload:any) {
        return new Promise((resolve,reject)=>{
            let rg_name = payload.rg_name || undefined
            let repo_group_id = payload.repo_group_id || undefined
            let group:RepoGroup = context.state.AugurAPI.RepoGroup({repo_group_id:repo_group_id,rg_name:rg_name})

            context.commit('mutateRepoGroup', {group:group, rg_name:rg_name})
        })
    }
};

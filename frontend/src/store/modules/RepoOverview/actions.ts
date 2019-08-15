import Repo from '@/AugurAPI';
import RepoGroup from '@/AugurAPI';
export default {
    async createAPIObjects(context: any, payload: any) {
        try {
            let apiGroups = context.state.getRepoGroups || {};
            let apiRepos = context.state.getRepos || {};
            if ('repos' in payload) {
                payload.repos.forEach((repo: any) => {
                    apiRepos[repo.url] = context.state.AugurAPI.Repo({gitURL: repo.url,
                        repo_id:repo.repo_id})
                })
            }
            if ('groups' in payload) {
                payload.groups.forEach((group: any) => {
                    apiGroups[group.rg_name] = context.state.AugurAPI.RepoGroup({rg_name: 
                        group.rg_name, repo_group_id: group.repo_group_id})
                })
            }
            context.commit('update_properties', {
                property: 'apiRepos',
                with: apiRepos,
            });
            context.commit('update_properties', {
                property: 'apiGroups',
                with: apiGroups,
            });
        } catch (error) {
            throw error;
        }
    },
    async endpoint(context: any, payload: any) {
        try {
            return new Promise((resolve, reject) => {
                let tempCache = context.state.cache || {};
                if ('endpoints' in payload) {
                    console.log(payload.endpoints)
                    if ('repos' in payload) {
                        context.state.AugurAPI.batchMapped(payload.repos, payload.endpoints).then(
                            (data: object[]) => {
                                console.log(data)
                                tempCache = {...tempCache, ...data};
                                payload.repos.forEach((repo: any) => {
                                    tempCache[repo.url] = {...tempCache[repo.url], ...data[repo.url]};
                                });
                            });
                    }
                    if ('repoGroups' in payload) {
                        context.state.AugurAPI.batchMapped(payload.repoGroups, payload.endpoints).then(
                            (data: object[]) => {
                                tempCache = {...tempCache, ...data};
                                payload.repoGroups.forEach((group: any) => {
                                    tempCache[group.rg_name] = {...tempCache[group.rg_name],
                                        ...data[group.rg_name]};
                                });
                            });
                    }
                    if (!('repos' in payload) && !('repoGroups' in payload)) {
                        payload.endpoints.forEach((endpoint: string) => {
                            console.log(endpoint)
                            context.state.AugurAPI[endpoint]().then((data: object[]) => {
                                tempCache[endpoint] = data;
                            });
                        });
                    }
                }
                console.log(tempCache)
                resolve(tempCache)
                // context.commit('mutate', {
                //     property: 'cache',
                //     with: tempCache,
                // });
                // resolve(tempCache)
            });
        } catch (error) {
            throw error;
        }
    },
};

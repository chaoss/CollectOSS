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
    async loadRepos(context:any, payload:any){
        try {
            return new Promise((resolve, reject) => {
                context.state.AugurAPI.getRepos().then((repos: object[]) => {
                    context.commit('mutateCache', {
                        property: 'getRepos',
                        with: repos,
                    });
                    resolve(repos)
                });
            })
        } catch(error) {
            throw error;
        }
    },
    async loadRepoGroups(context:any, payload:any){
        try {
            return new Promise((resolve, reject) => {
                context.state.AugurAPI.getRepoGroups().then((rgs: object[]) => {
                    context.commit('mutateCache', {
                        property: 'getRepoGroups',
                        with: rgs,
                    });
                    resolve(rgs)
                });
            })
        } catch(error) {
            throw error;
        }
    },
    // async loadRepoRelations(context:any, payload:any){
    //     try {

    //         context.dispatch('loadRepoGroups').then(() => {
    //             context.state.getters.repoGroups.forEach((group: any): void => {
    //                 repoGroups[group.rg_name] = group
    //                 repoRelations[group.rg_name] = {};
    //                 repos.filter((repo: any) => {
    //                     return repo.rg_name === group.rg_name;
    //                 }).forEach((repo: any) => {
    //                     repoRelations[group.rg_name][repo.url] = repo
    //                 });
    //             });
    //             context.commit('mutateCache', {
    //                 property: 'repoRelations',
    //                 with: repoRelations,
    //             });
    //         })
    //     } catch(error) {
    //         throw error;
    //     }
    // },
    // getRepoRelations(context: any, payload: object) {
    //     return new Promise ((resolve, reject) => {
    //         setTimeout(() => {
    //             let repoRelations = context.state.cache.getRepos || {};
    //             let repoGroups = context.state.cache.getRepoGroups || {};
    //             context.state.AugurAPI.getRepos().then((repos: object[]) => {
    //                 context.state.AugurAPI.getRepoGroups().then((groups: object[]) => {
    //                     // Move down between future relation endpoint
    //                     groups.forEach((group: any): void => {
    //                         repoGroups[group.rg_name] = group
    //                         repoRelations[group.rg_name] = {};
    //                         repos.filter((repo: any) => {
    //                             return repo.rg_name === group.rg_name;
    //                         }).forEach((repo: any) => {
    //                             repoRelations[group.rg_name][repo.url] = repo
    //                         });
    //                     });
    //                     context.commit('mutateCache', {
    //                         property: 'repoRelations',
    //                         with: repoRelations,
    //                     });
    //                     context.commit('mutateCache', {
    //                         property: 'repoGroups',
    //                         with: repoGroups,
    //                     });
    //                 });
    //             resolve({ repoRelations, repoGroups });
    //             });
    //         }, 2000)
    //     })
    // },
    async addRepo(context:any, payload:any) {
         return new Promise((resolve, reject) => {
             setTimeout(()=>{
                let rg_name = payload.rg_name || undefined
                let repo_id = payload.repo_id || undefined
                let repo_group_id = payload.repo_group_id || undefined
                let gitURL = payload.url || undefined
                let repo:Repo = context.state.AugurAPI.Repo({gitURL:gitURL,repo_id:repo_id,repo_group_id:repo_group_id})
                
                context.commit('mutateAPIRepo', {repo:repo, url: gitURL})
                resolve(repo)
             },2000)
         })
    },
    async addRepoGroup(context:any, payload:any) {
        return new Promise((resolve,reject)=>{
            let rg_name = payload.rg_name || undefined
            let repo_group_id = payload.repo_group_id || undefined
            let group:RepoGroup = context.state.AugurAPI.RepoGroup({repo_group_id:repo_group_id,rg_name:rg_name})

            context.commit('mutateAPIGroup', {group:group, rg_name:rg_name})
        })
    }
};

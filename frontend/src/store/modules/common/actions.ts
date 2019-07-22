import Repo from '@/AugurAPI';
import RepoGroup from '@/AugurAPI';
export default {
    async getRepoRelations(context: any, payload: object) {
        console.log(context.state);
        try {
            let repoRelations = context.state.cache.repoRelations || {};
            let repoGroups = context.state.cache.repoGroups || {};
            context.state.AugurAPI.getRepos().then((repos: object[]) => {
                context.state.AugurAPI.getRepoGroups().then((groups: object[]) => {
                    // Move down between future relation endpoint
                    groups.forEach((group: any): void => {
                        repoGroups[group.rg_name] = group//context.state.AugurAPI.RepoGroup(context.state.AugurAPI, group);
                        repoRelations[group.rg_name] = {};
                        repos.filter((repo: any) => {
                            return repo.rg_name === group.rg_name;
                        }).forEach((repo: any) => {
                            repoRelations[group.rg_name][repo.url] = repo
                                //context.state.AugurAPI.Repo({gitURL: repo.url}), repo_id: repo.repo_id})
                                // new Repo(context.state.AugurAPI, repo);
                        });
                        // THIS LINE WILL CHANGE WHEN WE IMPLEMENT A GROUP OBJECT OR CLASS
                        // repoGroups[group] = state.AugurAPI.Repo({gitURL: repo.url})
                    });
                    console.log(context)
                    context.commit('mutateCache', {
                        property: 'repoRelations',
                        with: repoRelations,
                    });
                    context.commit('mutateCache', {
                        property: 'repoGroups',
                        with: repoGroups,
                    });
                });
            });
            return { repoRelations, repoGroups };
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

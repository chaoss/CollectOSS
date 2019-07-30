/* tslint:disable */
import Vue from 'vue';
// import router from '@/router';

export default {
    setBaseRepo(state: any, payload: any) {
        // pass url into function
        state.baseRepo = payload.url
    },

    setBaseGroup(state: any, payload: any) {
        // pass url into function
        state.baseGroup = payload.rg_name
    },

    addComparedRepo(state:any, payload:any) {
        state.comparedRepos.push(payload)
    },

    addComparedRepoGroups(state:any, payload:any) {
        if(payload != null){
            state.comparedRepoGroups.push(payload)
        }
    },

    resetCompare(state:any, payload:any) {
        state.baseRepo = '';
        state.baseGroup = '';
        state.baseType = false;
        state.comparedRepos = [];
        state.comparedRepoGroups = [];
    },


    // addComparedRepo(state: any, payload: any) {
    //     state.compare = 'zscore'
    //     // state.hasState = true
    //
    //     let repo = state.AugurAPI.Repo(payload)
    //     if (!state.comparedRepos.includes(repo.toString()) && state.baseRepo != repo.toString()) {
    //         // if (!window.AugurRepos[repo.toString()]) {
    //         // window.AugurRepos[repo.toString()] = repo
    //         // } else {
    //         // repo = window.AugurRepos[repo.toString()]
    //         // }
    //         state.hasState = true
    //         if (repo.owner && repo.name) {
    //             state.comparedRepos.push(repo.toString())
    //             let title = repo.owner + '/' + repo.name + '- Augur'
    //         }
    //         if (payload.gitURL) {
    //             state.gitRepo = repo.gitURL
    //         }
    //         if (state.comparedRepos.length == 1) {
    //             if (!router.currentRoute.params.comparedrepo) {
    //
    //                 let owner = state.gitRepo ? null : state.baseRepo.substring(0, state.baseRepo.indexOf('/'))
    //                 let repo = state.gitRepo ? state.gitRepo : state.baseRepo.slice(state.baseRepo.indexOf('/') + 1)
    //                 let name = state.tab + "compare"
    //                 router.push({
    //                     name,
    //                     // params: {owner: owner, repo: repo, comparedowner: payload.owner, comparedrepo: payload.name}
    //                 })
    //             }
    //         } else {
    //             let groupid = (state.gitRepo ? String(state.gitRepo) + '+' : String(state.baseRepo) + "+")
    //             state.comparedRepos.forEach((repo: any) => {
    //                 groupid += (String(repo) + '+')
    //             })
    //             let name = state.tab + "group"
    //             router.push({
    //                 name,
    //                 params: {
    //                     groupid
    //                 }
    //             })
    //         }
    //     }
    // },

}
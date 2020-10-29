// #SPDX-License-Identifier: MIT
/* tslint:disable */
import Vue from 'vue';
import router from '@/router';

export default {
    mutate(state: any, payload: any) {
        Vue.set(state, payload.property, payload.with);
      },
    mutateBaseRepo(state: any, payload: any) {
        // pass url into function
            state.baseRepo = payload.url
    },

    mutateBaseGroup(state: any, payload: any) {
        // pass url into function
        state.baseGroup = payload.rg_name
    },

    mutateComparedRepo(state:any, payload:any) {
        if(payload != null){
            state.comparedRepos = []
            payload.forEach( (repo:any) => {
              state.comparedRepos.push(repo)
            });
        }
    },

    // setBaseRepo (state: any, payload: any) {
    //     console.log("HI",state)
    //     state.gitRepo = payload.url;
    //     state.baseRepo = payload.url;
    //     state.hasState = true;
    //     console.log(state)

    //     // let repo = state.AugurAPI.Repo(payload)
    //     // state.c
    //     // if (!AugurRepos[repo.toString()]) {
    //       // AugurRepos[repo.toString()] = repo
    //     // } else {
    //       // repo = AugurRepos[repo.toString()]
    //     // }
    //   },

    mutateComparedGroup(state:any, payload:any) {
        if(payload != null){
            state.comparedRepoGroups = []
            payload.forEach((group:any) => {
              state.comparedRepoGroups.push(group)
            })
        }
    },

    resetCompared (state: any) {
      state.comparedRepos = []
      state.comparedRepoGroups = []
    },

    setCompare(state:any, payload:any){
        state.compare = payload
    },
    setVizOptions (state:any, payload:any) {
        if (payload.trailingAverage) {
          state.trailingAverage = parseInt(payload.trailingAverage, 10)
        }
        if (typeof payload.rawWeekly !== 'undefined') {
          state.rawWeekly = payload.rawWeekly
        }
        if (typeof payload.showBelowAverage !== 'undefined') {
          state.showBelowAverage = payload.showBelowAverage
        }
        if (typeof payload.showArea !== 'undefined') {
          state.showArea = payload.showArea
        }
        if (typeof payload.showTooltip !== 'undefined') {
          state.showTooltip = payload.showTooltip
        }
        if (typeof payload.showDetail !== 'undefined') {
          state.showDetail = payload.showDetail
        }
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
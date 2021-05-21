// #SPDX-License-Identifier: MIT
/* tslint:disable */
import router from '@/router'
import Vue from 'vue';
import { VL_ONLY_GUIDE_CONFIG } from 'vega-lite/build/src/guide';
export default {
  update_properties(state: any, payload: any) {
    Vue.set(state, payload.property, {...state[payload.property], ...payload.with})//Object.assign(state.property, payload.with))
  },
  mutateCache(state: any, payload: any) {
    Vue.set(state.cache, payload.property, payload.with)
  },
  mutate (state: any, payload: any) {
    Vue.set(state, payload.property, payload.with);
  },
  setGitRepo (state: any, payload: any) {
    state.gitRepo = payload.gitURL
    state.baseRepo = payload.gitURL
    state.hasState = true
    let repo = null
    let repoName = gitUrlToString(payload)

    repo = state.AugurAPI.Repo(payload)
    state.baseRepo = repo.toString()
  },
  setRepo (state: any, payload: any) {
    let repoName = gitUrlToString(payload)
    let repo = null

    repo = state.AugurAPI.Repo(payload)

    state.hasState = true
    if (repo.owner && repo.name && !state.gitRepo) {
      state.baseRepo = repo.toString()
      let title = repo.owner + '/' + repo.name + '- Augur'
    }
    if (payload.gitURL) {
      state.gitRepo = repo.gitURL
      state.tab = state.tab ? state.tab : 'git'
    }
  },
  addComparedRepo (state: any, payload: any) {
    state.compare = 'zscore'
    state.hasState = true

    let repo = state.AugurAPI.Repo(payload)
    if(!state.comparedRepos.includes(repo.toString()) && state.baseRepo != repo.toString()){
      // if (!window.AugurRepos[repo.toString()]) {
        // window.AugurRepos[repo.toString()] = repo
      // } else {
        // repo = window.AugurRepos[repo.toString()]
      // }
      state.hasState = true
      if (repo.owner && repo.name) {
        state.comparedRepos.push(repo.toString())
        let title = repo.owner + '/' + repo.name + '- Augur'
      }
      if (payload.gitURL) {
        state.gitRepo = repo.gitURL
      }
      if (state.comparedRepos.length == 1) {
        if (!router.currentRoute.params.comparedrepo) {

          let owner = state.gitRepo ? null : state.baseRepo.substring(0, state.baseRepo.indexOf('/'))
          let repo = state.gitRepo ? state.gitRepo : state.baseRepo.slice(state.baseRepo.indexOf('/') + 1)
          let name = state.tab + "compare"
          router.push({
            name,
            // params: {owner: owner, repo: repo, comparedowner: payload.owner, comparedrepo: payload.name}
          })
        }
      } else {
        let groupid = (state.gitRepo ? String(state.gitRepo) + '+' : String(state.baseRepo) + "+")
        state.comparedRepos.forEach((repo: any) => {
          groupid += (String(repo) + '+')
        })
        let name = state.tab + "group"
        router.push({
          name,
          params: {
            groupid
          }
        })
      }
    }
  },
  mutateAPIRepo(state:any, payload:any) {
    Vue.set(state.apiRepos, payload.name, payload.repo)
  },
  mutateAPIGroup(state:any, payload:any) {
    Vue.set(state.apiGroups, payload.rg_name, payload.group)
  },
  mutateStartDate(state:any, payload:any) {
    state.startDate = payload;
  }, 
  mutateEndDate(state:any, payload:any) {
    state.endDate = payload;
  }, 
  // mutateStartDateChange(state:any, payload:any) {
  //   console.log('PAYLOAD: ');
  //   console.log(payload);
  //   // state.startDate = payload;
  //   Vue.set(state, 'startDate', payload);

  //   // console.log(state.startDate);
  // }
  // setDates (state: any, payload: any) {
  //   if (payload.startDate) {
  //     state.startDate = new Date(payload.startDate)
  //   }
  //   if (payload.endDate) {
  //     state.endDate = new Date(payload.endDate)
  //   }
  // },
  // setCompare (state: any, payload: any) {
  //   state.compare = payload.compare
  // },
  // setTab (state: any, payload: any) {
  //   state.tab = payload.tab
  //   state.hasState = true
  // },
  // setVizOptions (state: any, payload: any) {
  //   if (payload.trailingAverage) {
  //     state.trailingAverage = parseInt(payload.trailingAverage, 10)
  //   }
  //   if (typeof payload.rawWeekly !== 'undefined') {
  //     state.rawWeekly = payload.rawWeekly
  //   }
  //   if (typeof payload.showBelowAverage !== 'undefined') {
  //     state.showBelowAverage = payload.showBelowAverage
  //   }
  //   if (typeof payload.showArea !== 'undefined') {
  //     state.showArea = payload.showArea
  //   }
  //   if (typeof payload.showTooltip !== 'undefined') {
  //     state.showTooltip = payload.showTooltip
  //   }
  //   if (typeof payload.showDetail !== 'undefined') {
  //     state.showDetail = payload.showDetail
  //   }
  // },
  // resetComparedRepos (state: any) {
  //   state.comparedRepos = []
  //   router.push({
  //     name: state.tab,
  //     params: {owner: state.baseRepo.substring(0, state.baseRepo.indexOf('/')), repo: state.baseRepo.slice(state.baseRepo.indexOf('/') + 1)}
  //   })
  // },
  // resetBaseRepo (state: any) {
  //   state.baseRepo = ''
  // },
  // resetTab (state: any) {
  //   state.tab = ''
  // },
  // reset (state: any) {
  //   state = {
  //     baseRepo: '',
  //     hasState: false,
  //     tab: 'gmd',
  //     page: 'dashboard',
  //     gitRepo: '',
  //     comparedRepoGroups: new Array(),
  //     comparedRepos: new Array(),
  //     trailingAverage: 180,
  //     startDate: new Date('1 January 2005'),
  //     endDate: new Date(),
  //     compare: 'each',
  //     showBelowAverage: false,
  //     rawWeekly: false,
  //     showArea: true,
  //     showDetail: false,
  //     showTooltip: true,
  //     byDate: false
  //   }
  //   window.history.pushState(null, 'Augur', '/')
  // } // end reset
} // end mutations

function gitUrlToString(optipns:{githubURL?:string, gitURL?:string}){
  let owner = null
  let name = null
  if (optipns.githubURL) {
    let splitURL = optipns.githubURL.split('/')
    if (splitURL.length < 3) {
      owner = splitURL[0]
      name = splitURL[1]
    } else {
      owner = splitURL[3]
      name = splitURL[4]
    }
  }

  if (optipns.gitURL) {
    if (optipns.gitURL.includes('github.com')) {
      let splitURL = optipns.gitURL.split('/')
      owner = splitURL[1]
      name = splitURL[2].split('.')[0]
    } else {
      let splitURL = optipns.gitURL.split('/')
      owner = splitURL[0]
      name = splitURL[1]
    }
  }

  if (owner && name) {
    return owner + '/' + name
  } else {
    return JSON.stringify(optipns)
  }
}

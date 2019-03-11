const queryString = require('query-string')

// import AugurApp from './components/AugurApp.vue'
// import router from './router/router'
// import AugurCards from './components/AugurCards.vue'


export default function Augur () {
  window.jQuery = require('jquery')
  window.Vue = require('vue')
  window.Vuex = require('vuex')
  window.VueVega = require('vue-vega').default
  let AugurAPI = require('AugurAPI').default
  window.AugurAPI = new AugurAPI()
  window.AugurRepos = {}
  window.AugurStats = require('AugurStats').default
  window.$ = window.jQuery
  window._ = require('lodash')
  window.d3 = require('d3')
  window.SvgSaver = require('svgsaver')
  window.VueRouter = require('vue-router')
  let router = require('./router/router').default


  window.AUGUR_CHART_STYLE = {
    brightColors: ['#FF3647', '#007BFF', '#DAFF4D', '#B775FF'],
    dullColors: ['#CCCCCC', '#CCE7F2', '#D4F0B0', '#D8C3E3']
  }

  let AugurApp = require('./components/AugurApp')

  window.Vue.use(window.Vuex)
  window.Vue.use(window.VueVega)
  window.Vue.use(window.VueRouter)
  window.Vue.config.productionTip = false



  window.augur = new window.Vuex.Store({
    state: {
      hasState: null,
      tab: 'gmd',
      baseRepo: null,
      gitRepo: null,
      comparedRepos: [],
      trailingAverage: 180,
      startDate: new Date('1 February 2011'),
      endDate: new Date(),
      compare: 'rolling',
      showBelowAverage: false,
      rawWeekly: false,
      showArea: true,
      showDetail: true,
      showTooltip: true,
      byDate: false
    },
    mutations: {
      setGitRepo(state, payload) {
        state.gitRepo = payload.gitURL
        state.baseRepo = payload.gitURL
        state.hasState = true
        let repo = window.AugurAPI.Repo(payload)
        if (!window.AugurRepos[repo.toString()]) {
          window.AugurRepos[repo.toString()] = repo
        } else {
          repo = window.AugurRepos[repo.toString()]
        }
      },
      setRepo (state, payload) {
        let repo = window.AugurAPI.Repo(payload)
        if (!window.AugurRepos[repo.toString()]) {
          window.AugurRepos[repo.toString()] = repo
        } else {
          repo = window.AugurRepos[repo.toString()]
        }
        state.queryObject = {}
        state.hasState = true
        if (repo.owner && repo.name && !state.gitRepo) {
          state.baseRepo = repo.toString()
          let title = repo.owner + '/' + repo.name + '- Augur'
          // state.tab = 'gmd'
          // state.queryObject['repo'] = repo.owner + '+' + repo.name
        }
        if (payload.gitURL) {
          // state.queryObject['git'] = window.btoa(repo.gitURL)
          // state.tab = 'git'
          state.gitRepo = repo.gitURL
          state.tab = state.tab ? state.tab : 'git'
        }
      },
      // removeComparedRepo (state, payload) {
      //   state.comparedRepos
      // },
      addComparedRepo (state, payload) {
        state.compare = 'zscore'
        state.hasState = true
        let repo = window.AugurAPI.Repo(payload)
        if(!state.comparedRepos.includes(repo.toString()) && state.baseRepo != repo.toString()){
          if (!window.AugurRepos[repo.toString()]) {
            window.AugurRepos[repo.toString()] = repo
          } else {
            repo = window.AugurRepos[repo.toString()]
          }
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
                params: {owner, repo, comparedowner: payload.owner, comparedrepo: payload.name}
              })
            }
          } else {
            let groupid = (state.gitRepo ? String(state.gitRepo) + '+' : String(state.baseRepo) + "+")
            state.comparedRepos.forEach((repo) => {
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
      setDates (state, payload) {
        if (payload.startDate) {
          state.startDate = new Date(payload.startDate)
        }
        if (payload.endDate) {
          state.endDate = new Date(payload.endDate)
        }
      },
      setCompare (state, payload) {
        state.compare = payload.compare
      },
      setTab (state, payload) {
        state.tab = payload.tab
        state.hasState = true
      },
      setVizOptions (state, payload) {
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
      resetComparedRepos (state) {
        state.comparedRepos = []
        router.push({
          name: state.tab,
          params: {owner: state.baseRepo.substring(0, state.baseRepo.indexOf('/')), repo: state.baseRepo.slice(state.baseRepo.indexOf('/') + 1)}        })
      },
      resetBaseRepo (state) {
        state.baseRepo = null
      },
      resetTab (state) {
        state.tab = null
      },
      reset (state) {
        state = {
          baseRepo: null,
          comparedRepo: null,
          trailingAverage: 180,
          startDate: new Date('1 January 2005'),
          endDate: new Date(),
          compare: 'each',
          byDate: false
        }
        window.history.pushState(null, 'Augur', '/')
      } // end reset
    } // end mutations
  })

  AugurApp.store = window.augur

  router.beforeEach((to, from, next) => {
    if (to.params.repo || to.params.groupid){
      if (!to.params.groupid && !to.params.comparedrepo){
        AugurApp.store.commit("resetTab")
        AugurApp.store.commit('setTab', {
          tab: to.name
        })
        if (to.params.repo.includes('github') || to.params.repo.split(".").length > 2) {
          AugurApp.store.commit('setRepo', {
            gitURL: to.params.repo
          })
        } else {
          AugurApp.store.commit('setRepo', {
            githubURL: to.params.owner + '/' + to.params.repo
          })
        }
      } else if (to.params.comparedrepo && augur.state.comparedRepos.length == 0) { 
        let tab = to.name
        tab = tab.substring(0, tab.length-7)
        AugurApp.store.commit("resetTab")
        AugurApp.store.commit('setTab', {
          tab
        })
        AugurApp.store.commit('setRepo', {
            githubURL: to.params.owner + '/' + to.params.repo
          })
        AugurApp.store.commit('addComparedRepo', {
          githubURL: to.params.comparedowner + '/' + to.params.comparedrepo
        })
      } else if (to.params.groupid && augur.state.comparedRepos.length == 0){
        AugurApp.store.commit("resetTab")
        let tab = to.name
        tab = tab.substring(0, tab.length-5)
        AugurApp.store.commit('setTab', {
          tab
        })
        let repos = to.params.groupid.split('+')
        if (repos[0].includes('github')) {
          AugurApp.store.commit('setRepo', {
            gitURL: repos[0]
          })
        } else {
          AugurApp.store.commit('setRepo', {
            githubURL: repos[0]
          })
        }
        repos.shift()
        // repos.pop()
        repos.forEach((cmprepo) => {
          AugurApp.store.commit('addComparedRepo', {
            githubURL: cmprepo
          })
        })
      }
    }

    next()
  })

    
  window.AugurApp = new window.Vue({
    // components: { AugurApp },
    // store: window.augur,
    router,
    render: h => h(AugurApp)

  }).$mount('#app')

  // Load state from query string

  // let parsed = queryString.parse(window.location.search, { arrayFormat: 'bracket' })
  // let payload = { fromURL: true }
  // let hasState = 0
  // if (parsed.repo) {
  //   payload.githubURL = parsed.repo.replace(' ', '/')
  //   hasState = 1
  // }
  // if (parsed.git) {
  //   payload.gitURL = window.atob(parsed.git)
  //   hasState = 1
  // }
  // if (hasState) {
  //   window.AugurApp.$store.commit('setRepo', payload)
  // }
  // if (parsed.comparedTo) {
  //   parsed.comparedTo.forEach((repo) => {
  //     window.AugurApp.$store.commit('addComparedRepo', { githubURL: repo.replace(' ', '/') })
  //   })
  // }
}

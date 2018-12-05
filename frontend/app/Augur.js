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
      startDate: new Date('1 January 2011'),
      endDate: new Date(),
      compare: 'baseline',
      showBelowAverage: false,
      rawWeekly: false,
      showArea: true,
      showDetail: true,
      showTooltip: true,
      byDate: false
    },
    mutations: {
      setGitRepo(state, payload) {
        console.log("hi",payload)
        state.gitRepo = payload.gitURL
        state.hasState = true
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
        if (repo.owner && repo.name) {
          state.baseRepo = repo.toString()
          let title = repo.owner + '/' + repo.name + '- Augur'
          state.tab = 'gmd'
          // state.queryObject['repo'] = repo.owner + '+' + repo.name
        }
        if (payload.gitURL) {
          // state.queryObject['git'] = window.btoa(repo.gitURL)
          state.tab = 'git'
          state.gitRepo = repo.gitURL
        }
        if (!payload.fromURL){
            // window.history.pushState(null, 'Augur', ('?' + queryString.stringify(state.queryObject, {encode: false})))
          
        }



        // if (!payload.keepCompared) {
        //   state.comparedRepos = []
        // }
      },
      addComparedRepo (state, payload) {
        // //let repo = window.AugurAPI.Repo({ githubURL: payload.url })
        // let repo = window.AugurAPI.Repo(payload)

        // if (!window.AugurRepos[repo.toString()]) {
        //   window.AugurRepos[repo.toString()] = repo
        // }
        // //state.comparedRepos.push(repo.toString())
        // state.comparedTo = repo.toString()
        // let title = 'Augur'
        // let queryString = window.location.search + '&comparedTo[]=' + repo.owner + '+' + repo.name
        // window.history.pushState(null, title, queryString)
        state.compare = 'zscore'
        state.hasState = true
        let repo = window.AugurAPI.Repo(payload)
        console.log("fook", state.comparedRepos, repo.toString(), !state.comparedRepos.includes(repo.toString()) && state.baseRepo != repo.toString())
        if(!state.comparedRepos.includes(repo.toString()) && state.baseRepo != repo.toString()){
        // if(false){
          console.log("hiiiii", router.app._route.params.comparedowner + '/' + router.app._route.params.comparedowner, router)
          //(!this.$route.params.comparedowner) {
          if (state.comparedRepos.length + 1 == 1) {
            if (!router.app._route.params.comparedowner) {
              let link = router.app._route.path + '/comparedto/' + payload

              router.push({
                path: link
                // path: "/git"
              })
            }
          } else {
            let link = '/' + state.tab + '/groupid/-1'
            router.push({
              path: link
              // path: "/git"
            })
          }
          
          if (!window.AugurRepos[repo.toString()]) {
            
            window.AugurRepos[repo.toString()] = repo
          } else {
            repo = window.AugurRepos[repo.toString()]
          }
          state.hasState = true
          if (repo.owner && repo.name) {
            state.comparedRepos.push(repo.toString())
            let title = repo.owner + '/' + repo.name + '- Augur'
            // state.tab = 'gmd'
            // let queryString = window.location.search + '&comparedTo[]=' + repo.owner + '+' + repo.name
            // window.history.pushState(null, title, queryString)
          }
          if (payload.gitURL) {
            // let queryString = '&git=' + window.btoa(repo.gitURL)
            // window.history.pushState(null, 'Git Analysis - Augur', window.location.search + queryString)
            // state.tab = 'git'
            state.gitRepo = repo.gitURL
          }
          // if (state.comparedRepos.length == 1) {
          // let link = this.$router.currentRoute + '/comparedto/' + e.target.value
          //   this.$router.push({
          //     path: link
          //     // path: "/git"
          //   })
          // } else {
          //   let link = '/groupid/'
          //   this.$router.push({
          //     path: link
          //     // path: "/git"
          //   })
          // }
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
  
  
  
  // AugurApp.router = router
  // AugurApp.render = h => h(AugurApp)

  // window.AugurApp = new window.Vue(AugurApp).$mount('#app')
  
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

import VueVega from 'vue-vega'
const queryString = require('query-string')

export default function Augur () {
  window.jQuery       = require('jquery')
  window.Vue          = require('vue')
  window.Vuex         = require('vuex')
  let AugurAPI       = require('AugurAPI').default
  window.AugurAPI    = new AugurAPI()
  window.AugurRepos  = {}
  window.AugurStats  = require('AugurStats').default
  window.$            = window.jQuery
  window._            = require('lodash')
  window.d3           = require('d3')
  window.VueVega      = VueVega
  window.SvgSaver     = require('svgsaver')

  let AugurApp = require('./components/AugurApp')

  Vue.use(Vuex)
  Vue.use(VueVega)
  Vue.config.productionTip = false

  window.augur = new Vuex.Store({
    state: {
      baseRepo: null,
      comparedRepos: [],
      trailingAverage: 180,
      startDate: new Date("1 January 2005"),
      endDate: new Date(),  
      compare: "each",
      showBelowAverage: false,
      rawWeekly: false,
      byDate: false,
    },
    mutations: {
      setBaseRepo (state, payload)  {
        let repo = window.AugurAPI.Repo(payload.url)
        if (!window.AugurRepos[repo.toString()]) {
          window.AugurRepos[repo.toString()] = repo
        }
        state.baseRepo = repo.toString()
        if (!payload.keepCompared) {
          state.comparedRepos = []
        }
        let title = repo.owner + '/' + repo.name + '- Augur' 
        let queryString = '?repo=' + repo.owner + '+' + repo.name
        window.history.pushState(null, title, queryString)
      },
      addComparedRepo (state, payload) {
        let repo = window.AugurAPI.Repo(payload.url)
        if (!window.AugurRepos[repo.toString()]) {
          window.AugurRepos[repo.toString()] = repo
        }
        state.comparedRepos.push(repo.toString())
        let title = 'Augur' 
        let queryString = window.location.search + '&comparedTo[]=' + repo.owner + '+' + repo.name
        window.history.pushState(null, title, queryString)
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
      },
      reset (state) {
        state = {
          baseRepo: null,
          comparedRepos: [],
          trailingAverage: 180,
          startDate: new Date("1 January 2005"),
          endDate: new Date(),
          compare: "each",
          byDate: false,
        }
        window.history.pushState(null, 'Augur', '/')
      } // end reset
    } // end mutations
  })

  AugurApp.store = window.augur
  window.AugurApp = new Vue(AugurApp).$mount('#app')

  // Load state from query string
  let parsed = queryString.parse(location.search, { arrayFormat: 'bracket' })
  if (parsed.repo) {
    window.AugurApp.$store.commit('setBaseRepo', { url: parsed.repo.replace(' ', '/') })
  }
  if (parsed.comparedTo) {
    parsed.comparedTo.forEach((repo) => {
      window.AugurApp.$store.commit('addComparedRepo', { url: repo.replace(' ', '/') })
    })
  }

}
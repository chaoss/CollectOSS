const queryString = require('query-string')

export default function GHData () {
  window.jQuery       = require('jquery')
  window.Vue          = require('vue')
  window.Vuex         = require('vuex')
  let GHDataAPI       = require('GHDataAPI').default
  window.GHDataAPI    = new GHDataAPI()
  window.GHDataRepos  = {}
  window.GHDataStats  = require('GHDataStats').default
  window.$            = window.jQuery
  window.d3           = require('d3')
  window.SvgSaver     = require('svgsaver')

  let GHDataApp = require('./components/GHDataApp')

  Vue.use(Vuex)

  window.ghdata = new Vuex.Store({
    state: {
      baseRepo: null,
      comparedRepos: [],
      trailingAverage: 180,
      startDate: new Date("1 January 2005"),
      endDate: new Date(),  
      compare: "each",
      byDate: false,
    },
    mutations: {
      setBaseRepo (state, payload)  {
        let repo = window.GHDataAPI.Repo(payload.url)
        if (!window.GHDataRepos[repo.toString()]) {
          window.GHDataRepos[repo.toString()] = repo
        }
        state.baseRepo = repo.toString()
        if (!payload.keepCompared) {
          state.comparedRepos = []
        }
        let title = repo.owner + '/' + repo.name + '- GHData' 
        let queryString = '?repo=' + repo.owner + '+' + repo.name
        window.history.pushState(null, title, queryString)
      },
      addComparedRepo (state, payload) {
        let repo = window.GHDataAPI.Repo(payload.url)
        if (!window.GHDataRepos[repo.toString()]) {
          window.GHDataRepos[repo.toString()] = repo
        }
        state.comparedRepos.push(repo.toString())
        let title = 'GHData' 
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
        if (payload.trailingAverage) {
          state.trailingAverage = parseInt(payload.trailingAverage, 10)
        }
      },
      setCompare (state, payload) {
        state.compare = payload.compare
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
        window.history.pushState(null, 'GHData', '/')
      } // end reset
    } // end mutations
  })

  GHDataApp.store = window.ghdata
  window.GHDataApp = new Vue(GHDataApp).$mount('#app')

  // Load state from query string
  let parsed = queryString.parse(location.search, { arrayFormat: 'bracket' })
  if (parsed.repo) {
    window.GHDataApp.$store.commit('setBaseRepo', { url: parsed.repo.replace(' ', '/') })
  }
  if (parsed.comparedTo) {
    parsed.comparedTo.forEach((repo) => {
      window.GHDataApp.$store.commit('addComparedRepo', { url: repo.replace(' ', '/') })
    })
  }

}
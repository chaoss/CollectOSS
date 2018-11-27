import Vue from 'vue'
import Router from 'vue-router'

const routes = [
      {path: '/', component: Vue.component('augur-cards',require('../components/AugurCards'))},
      // {path: '/', component: 'AugurApp'},
      // {path: '/gmd', component: GrowthMaturityDeclineCard},
      // {path: '/exp', component: ExperimentalCard}
    ]
Vue.use(Router)
export default new Router({
  routes,
  mode: 'history'
})

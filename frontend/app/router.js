import AugurCards from './components/AugurCards'
import GrowthMaturityDeclineCard from './components/GrowthMaturityDeclineCard'
import ExperimentalCard from './components/ExperimentalCard'
import VueRouter from 'vue-router'
import Vue from 'vue'

Vue.use(VueRouter)
 


export default new VueRouter({
  routes: [
      {path: '/', component: Vue.component('augur-cards',require('./components/AugurCards'))},
      // {path: '/gmd', component: GrowthMaturityDeclineCard},
      // {path: '/exp', component: ExperimentalCard}
    ]
})

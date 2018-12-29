import Vue from 'vue'
import Router from 'vue-router'
import AugurCards from '../components/AugurCards.vue'
import MetricsStatusCard from '../components/MetricsStatusCard.vue'
import GitCard from '../components/GitCard.vue'
import ExperimentalCard from '../components/ExperimentalCard.vue'
import GrowthMaturityDeclineCard from '../components/GrowthMaturityDeclineCard.vue'

let routes = [
  {path: '/', component: AugurCards},
      {path: '/metrics_status', component: MetricsStatusCard},
      // {path: '/:tab/:owner/:repo', component: AugurCards, name: 'single'},
      {path: '/single/:tab/:owner?/:repo/:domain?', component: AugurCards, name: 'single', props: true},
      // {path: '/:tab/:domain/:owner/:repo/comparedto/:comparedowner/:comparedrepo', component: AugurCards, name: 'gitsinglecompare'},
      {path: '/compare/:tab/:owner?/:repo/:domain?/comparedto/:comparedowner/:comparedrepo/:compareddomain?', component: AugurCards, name: 'singlecompare', props: true},
      // {path: '/:tab/:owner/:repo/comparedto/:comparedowner/:comparedrepo', component: AugurCards, name: 'singlecompare'},
      {path: '/groupcompare/:tab/:groupid', component: AugurCards, name: 'group', props: true},
]
let downloadedRepos = [], repos = [], projects = []
window.AugurAPI.getDownloadedGitRepos().then((data) => {

  repos = window._.groupBy(data, 'project_name')
  projects = Object.keys(repos)

})
// const routes = routerOptions.map(route => {
//   // let route1 = Object.assign({}, route);
//   return {
//     route,
//     component: () => require(`@/components/${route.component}.vue`)
//   }
// })


export default new Router({
  // routes,
  routes,
  mode: 'history'
})
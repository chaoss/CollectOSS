// #SPDX-License-Identifier: MIT
// import queryString from 'query-string';
// import Vuex from 'vuex';
// import VueRouter from 'vue-router'

/* tslint:disable */
import { createApp } from 'vue';
import ShardsVue from 'shards-vue';
import VueVega from 'vue-vega';
import _ from 'lodash';
import NProgress from 'nprogress'
// Styles
import "../node_modules/bootstrap/scss/bootstrap.scss";
import '@/styles/shards-dashboards.scss';
import '@/assets/scss/date-range.scss';
import 'nprogress/nprogress.css'
import './styles/augur.styl'
// Core
import AugurApp from '@/components/AugurApp.vue';
import router from './router';
import { store } from './store/store'

// Layouts
import Default from '@/layouts/Default.vue';

// Utility
import AugurAPI from '@/AugurAPI';
import AugurStats from '@/AugurStats';



export default function Augur() {
  // AugurApp.store = store
  // Object.defineProperty(AugurApp, 'store', store);

  router.beforeEach((to: any, from: any, next: any) => {
    NProgress.start()
    NProgress.set(0.4);
    store.commit('common/mutate', { property: 'tab', with: to.name })
    if (to.name == 'inspect_insight' && !('metric' in to.params)) {
      to.params.metric = from.params.metric
    }
    if (!to.params.repo && !to.params.group) {
      if (!to.params.compares) {
        store.commit('compare/resetCompared')
      }
      store.dispatch('compare/setBaseRepo', {
        rg_name: to.params.group,
        repo_name: to.params.repo,
        repo_group_id: to.params.repo_group_id,
        repo_id: to.params.repo_id,
        gitURL: to.params.url
      }).then((data: any) => {
        return store.dispatch('compare/setBaseGroup', {
          rg_name: to.params.group,
          repo_name: to.params.repo,
          repo_group_id: to.params.repo_group_id,
          repo_id: to.params.repo_id,
          gitURL: to.params.url
        })
      }).finally(() => {
        next()
      })
    } else if (to.params.group && to.params.repo) {
      console.log("bout to", to.params, !to.params.repo_group_id || !to.params.repo_id)
      NProgress.set(0.6);
      let repo_group_id = null
      let repo_id = null
      let loaded = false
      if (!to.params.repo_group_id || !to.params.repo_id) {
        store.dispatch('common/retrieveRepoIds', {
          repo: to.params.repo,
          rg_name: to.params.group
        }).then((ids: any) => {
          repo_group_id = ids['repo_group_id']
          repo_id = ids['repo_id']
          store.dispatch('compare/setBaseRepo', {
            rg_name: to.params.group,
            repo: to.params.repo,
            repo_group_id: repo_group_id,
            repo_id: repo_id
          }).then(() => {
            NProgress.set(0.8);

            if (to.params.compares) {
              if (to.params.compares != 'none_selected') {


                console.log("HERE,", store)
                let compares = !to.params.compares ? [] : to.params.compares.split(',');
                let ids = !to.params.comparedRepoIds ? [] : to.params.comparedRepoIds.split(',');
                store.dispatch('compare/setComparedRepos', { 'names': compares, 'ids': ids }).then(() => {
                  next()
                })
                // return store.dispatch('compare/setComparedRepos', { 'names': compares, 'ids': ids })
              }
            } else {
              loaded = true
            }
          }).finally(() => {
            if (loaded)
              next()
          })
        })
      } else {
        store.dispatch('compare/setBaseRepo', {
          rg_name: to.params.group,
          repo: to.params.repo,
          repo_group_id: to.params.repo_group_id,
          repo_id: to.params.repo_id
        }).then(() => {
          NProgress.set(0.8);
          if (to.params.compares) {
            let compares = to.params.compares === '' ? [] : to.params.compares.split(',');
            let ids = to.params.comparedRepoIds === '' ? [] : to.params.comparedRepoIds.split(',');
            store.dispatch('compare/setComparedRepos', { 'names': compares, 'ids': ids })
            // return store.dispatch('compare/setComparedRepos', { 'names': compares, 'ids': ids })
          }
        }).finally(() => {
          next()
        })
      }

    } else if (to.params.group && !to.params.repo) {
      NProgress.set(0.6)
      store.dispatch('compare/setBaseGroup', {
        rg_name: to.params.group,
        repo_group_id: to.params.repo_group_id
      }).then((data: any) => {
        NProgress.set(0.8);
        if (to.params.compares) {
          let compares = to.params.compares === '' ? [] : to.params.compares.split(',');
          return store.dispatch('compare/setComparedGroup', compares)
        }
      }).finally(() => {
        next()
      })
    } else {
      next()
    }
  })

  router.afterEach(() => {
    // 在即将进入新的页面组件前，关闭掉进度条
    NProgress.done()
  })

  // router.beforeEach((to:any, from:any, next:any) => {
  //   if (to.params.repo || to.params.groupid){
  //     if (!to.params.groupid && !to.params.comparedrepo){
  //       AugurApp.store.commit("resetTab")
  //       AugurApp.store.commit('setTab', {
  //         tab: to.name
  //       })
  //       if (to.params.repo.includes('github') || to.params.repo.split(".").length > 2) {
  //         AugurApp.store.commit('setRepo', {
  //           gitURL: to.params.repo
  //         })
  //       } else {
  //         AugurApp.store.commit('setRepo', {
  //           githubURL: to.params.owner + '/' + to.params.repo
  //         })
  //       }
  //     } else if (to.params.comparedrepo && AugurApp.store.state.comparedRepos.length == 0) {
  //       let tab = to.name
  //       tab = tab.substring(0, tab.length-7)
  //       AugurApp.store.commit("resetTab")
  //       AugurApp.store.commit('setTab', {
  //         tab
  //       })
  //       AugurApp.store.commit('setRepo', {
  //           githubURL: to.params.owner + '/' + to.params.repo
  //         })
  //       AugurApp.store.commit('addComparedRepo', {
  //         githubURL: to.params.comparedowner + '/' + to.params.comparedrepo
  //       })
  //     } else if (to.params.groupid && AugurApp.store.state.comparedRepos.length == 0){
  //       AugurApp.store.commit("resetTab")
  //       let tab = to.name
  //       tab = tab.substring(0, tab.length-5)
  //       AugurApp.store.commit('setTab', {
  //         tab
  //       })
  //       let repos = to.params.groupid.split('+')
  //       if (repos[0].includes('github')) {
  //         AugurApp.store.commit('setRepo', {
  //           gitURL: repos[0]
  //         })
  //       } else {
  //         AugurApp.store.commit('setRepo', {
  //           githubURL: repos[0]
  //         })
  //       }
  //       repos.shift()
  //       // repos.pop()
  //       repos.forEach((cmprepo:string) => {
  //         AugurApp.store.commit('addComparedRepo', {
  //           githubURL: cmprepo
  //         })
  //       })
  //     }
  //   }

  //   next()
  // })

  // AugurApp.storeApp = new window.Vue({

  const app = createApp({
    router,
    store,
    render: h => h(AugurApp)
  })

  app.use(router)
  app.use(store)
  ShardsVue.install(app);
  app.component('default-layout', Default);
  app.use(ShardsVue);
  app.use(VueVega);

  app.mount("#app")
}

Augur()
// #SPDX-License-Identifier: MIT
import Vue from 'vue'
import VueRouter from 'vue-router'
// import Login from '../layouts/Login/Login.vue';
// import Dashboard from '../layouts/Dashboard/Dashboard.vue';
import ManageRepos from '../layouts/ManageRepos/ManageRepos.vue';
// import AnalyzeRepos from '../components/Dashboard/AnalyzeRepos/AnalyzeRepos.vue';
// import AboutAugur from '../layouts/AboutAugur/AboutAugur.vue';
// import SlackConfig from '../layouts/SlackConfig/SlackConfig.vue';

Vue.use(VueRouter)

// previous version anticipated several routes
//
// const routes = [
//   {
//     path: '/',
//     name: 'login',
//     component: Login
//   },
//   {
//     path: '/dashboard',
//     name: 'dashboard',
//     component: Dashboard, 
//     children: [
//       {
//         path: 'manage', 
//         component: ManageRepos, 
//         name: 'manage'
//       }, 
//       {
//         path: 'slack', 
//         component: SlackConfig, 
//         name: 'slack'
//       }, 
//       // {
//       //   path: 'analyze', 
//       //   component: AnalyzeRepos
//       // }, 
//       {
//         path: 'about', 
//         component: AboutAugur, 
//         name: 'about'
//       }
//     ]
//   }
// ]

const routes = [
  {
    path: '/', 
    name: 'manage', 
    component: ManageRepos
  }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router

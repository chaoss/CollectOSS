import Vue from 'vue'
import VueRouter from 'vue-router'
import Login from '../components/Login/Login.vue';
// import Dashboard from '../views/Dashboard.js';

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    name: 'login',
    component: Login
  },
  // {
  //   path: '/dashboard',
  //   name: 'dashboard',
  //   component: Dashboard
  // }
]

const router = new VueRouter({
  mode: 'history',
  base: process.env.BASE_URL,
  routes
})

export default router

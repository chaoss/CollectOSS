import Vue from 'vue'
import VueRouter from 'vue-router'
import SlackLogin from "../components/SlackLogin.vue";
import SlackConfig from "../components/SlackConfig.vue";
import Auth from "../components/Auth.vue";

Vue.use(VueRouter)

  const routes = [
  {
    path: '/', 
    component: Auth, 
    name: 'auth'
  }, 
  {
    path: '/login',
    name: 'slack-login',
    component: SlackLogin
  },
  {
    path: '/configure',
    name: 'slack-config',
    component: SlackConfig, 
    props: true
  }
]

const router = new VueRouter({
  routes
})

export default router

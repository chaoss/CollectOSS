import Vue from 'vue'
import VueRouter from 'vue-router'
import SlackLogin from "../components/SlackLogin.vue";
import SlackConfig from "../components/SlackConfig.vue";

Vue.use(VueRouter)

  const routes = [
  {
    path: '/login',
    name: 'slack-login',
    component: SlackLogin
  },
  {
    path: '/configure',
    name: 'slack-config',
    component: SlackConfig
  }
]

const router = new VueRouter({
  routes
})

export default router

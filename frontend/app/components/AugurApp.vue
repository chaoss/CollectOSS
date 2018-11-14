<template>
  <div>
    <augur-header></augur-header>
    <div class="content">
      <!-- <router-view></router-view> -->
      <augur-cards></augur-cards>
    </div>
  </div>
</template>

<script>

import AugurHeader from './AugurHeader.vue'
import AugurCards from './AugurCards.vue'
import VueRouter from 'vue-router'
import RouterView from 'vue-router'
import GrowthMaturityDeclineCard from './GrowthMaturityDeclineCard'
import ExperimentalCard from './ExperimentalCard'

Vue.use(VueRouter)

// const routes = [
//       {path: '/', component: GrowthMaturityDeclineCard},
//       {path: '/gmd', component: GrowthMaturityDeclineCard},
//       {path: '/exp', component: ExperimentalCard}
//     ]

// const router = new VueRouter({
//   routes
// })

module.exports = {
  // name: "augur-app",
  components: {
    'augur-header': AugurHeader,
    'augur-cards': AugurCards,
    // router,
    // 'router-view': RouterView
  }
}

</script>
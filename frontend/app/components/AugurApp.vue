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
// import router from '../router.js'
// import VueRouter from 'vue-router'
// import RouterView from 'vue-router'

module.exports = {
  // name: "AugurApp",
  components: {
    'augur-header': AugurHeader,
    'augur-cards': AugurCards,
    // router,
    // 'router-view': RouterView
  }
}

</script>
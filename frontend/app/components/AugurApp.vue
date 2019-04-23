<template>
  <div>
    
    <div id="app" class="content">
      <router-view></router-view>
      <!-- <augur-cards></augur-cards> -->
    </div>
  </div>
</template>

<script>

import AugurHeader from './AugurHeader.vue'
import AugurCards from './AugurCards.vue'
import VueRouter from 'vue-router'
// import RouterView from 'vue-router'
import GrowthMaturityDeclineCard from './GrowthMaturityDeclineCard'
import ExperimentalCard from './ExperimentalCard'


module.exports = {
  name: "app",
  components: {
    'augur-header': AugurHeader,
    'augur-cards': AugurCards,
  
  }
}

</script>

<style scoped>
@import 'shards-ui/dist/css/shards.css';
@import 'bootstrap/dist/css/bootstrap.css';
@import 'quill/dist/quill.snow.css';
</style>
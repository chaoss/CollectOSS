<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div>
    <div id="app">
      <router-view></router-view>
      <!-- <augur-cards></augur-cards> -->
    </div>
  </div>
</template>

<script lang='ts'>
import AugurHeader from "./AugurHeader.vue";
import AugurCards from "./AugurCards.vue";
import VueRouter from "vue-router";
import { store } from "../store/store";

export default {
  name: "app",
  components: {
    "augur-header": AugurHeader,
    "augur-cards": AugurCards,
  },
  store: store,
};
</script>
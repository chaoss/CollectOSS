<!-- #SPDX-License-Identifier: MIT -->
<template>
  <header id="DashboardHeader">
    <img src="../../../assets/logo.png" alt />
    <nav-bar :links="links"/>
  </header>
</template>

<script>
import NavBar from "./NavBar.vue";

export default {
  name: "DashboardHeader",
  data() {
    return {
      links: [
        { text: "MANAGE REPOS", path: "/dashboard/manage" },
        // { text: "ANALYZE REPOS", path: "/dashboard/analyze" },
        { text: "ABOUT AUGUR", path: "/dashboard/about" }
      ]
    };
  },
  components: {
    NavBar
  }
};
</script>

<style scoped>
header {
  background-color: white;
  box-shadow: 0 0 20px 0 var(--grey);
  z-index: 10;
  position: relative;
}

img {
  width: 250px;
}
</style>
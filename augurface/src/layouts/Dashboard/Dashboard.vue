<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="Dashboard">
    <dashboard-header />
    <transition name="fade" mode="out-in">
      <router-view />
    </transition>
  </div>
</template>

<script>
import DashboardHeader from "./dashboardHeader/DashboardHeader.vue";

export default {
  name: "Dashboard",
  components: {
    DashboardHeader
  },
  beforeCreate() {
    this.$store.dispatch("reposModule/retrieveRepoGroups", true);
    this.$store.dispatch("reposModule/retrieveRepos", true);
  }
};
</script>

<style>
</style>
<template>
  <div id="Dashboard">
      <dashboard-header />
      <router-view />
  </div>
</template>

<script>
import DashboardHeader from './dashboardHeader/DashboardHeader.vue';

export default {
    name: "Dashboard", 
    components: {
        DashboardHeader
    }, 
    beforeCreate() {
        this.$store.dispatch('reposModule/retrieveRepoGroups');
        this.$store.dispatch('reposModule/retrieveRepos');
    }
};
</script>

<style>
</style>
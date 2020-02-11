<template>
  <div id="ManageRepos">
    <manage-buttons />
    <repo-group v-for="rg in $store.state.reposModule.repoGroups" :key="rg.repo_group_id" :repoGroupObject="rg" />
  </div>
</template>

<script>
import RepoGroup from './repoGroup/RepoGroup.vue';
import ManageButtons from './ManageButtons.vue';

export default {
  name: "ManageRepos", 
  components: {
    RepoGroup, 
    ManageButtons
  }
};
</script>

<style scoped>
#ManageRepos {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 3rem;
  height: 2000px;
}

</style>
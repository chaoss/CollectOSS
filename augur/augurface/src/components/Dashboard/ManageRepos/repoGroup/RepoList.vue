<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div class="RepoList">
    <p>Repos</p>
    <repo
      v-for="repo in repos"
      :key="repo.repo_id"
      :repo="repo"
    />
  </div>
</template>

<script>
import Repo from "./Repo.vue";

export default {
    name: "RepoList", 
    components: {
        Repo
    }, 
    props: {
        repos: {
            type: Array, 
            required: true
        }
    }
};
</script>

<style scoped>
#RepoList {
  border-bottom: 1px solid var(--grey);
}

p {
  margin: 0 !important;
  margin-left: 1rem !important;
  padding: 0 !important;
}
</style>
<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="ManageRepos">
    <manage-buttons @collapseAll="collapseAll()"/>
    <div class="loading" v-if="!isLoaded">
      <img src="../../../assets/loading.gif" alt="loading repos" />
      <p>loading repositories...</p>
    </div>
    <div class="groups" v-if="isLoaded">
      <repo-group
        v-for="rg in getRepoGroups"
        :key="rg.repo_group_id"
        :repoGroup="rg"
        ref="repoGroups"
      />
    </div>
  </div>
</template>

<script>
import RepoGroup from "./repoGroup/RepoGroup.vue";
import ManageButtons from "./ManageButtons.vue";
import { mapGetters } from "vuex";

export default {
  name: "ManageRepos",
  components: {
    RepoGroup,
    ManageButtons
  },
  methods: {
    collapseAll() {
      this.$refs.repoGroups.forEach(rg => rg.collapse());
    }
  }, 
  computed: {
    ...mapGetters("reposModule", ["isLoaded", "isGroupsLoaded", "getRepoGroups"])
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

.groups {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.loading {
  margin-top: 2rem;
}

.loading > img {
  transform: translateX(-20px);
}

.loading > p {
  color: var(--dark-grey);
}
</style>
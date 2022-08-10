<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="ManageRepos">
    <dashboard-header />
    <div id="manage-content">
      <manage-buttons @collapseAll="collapseAll()" />
      <div class="loading" v-if="!isLoaded">
        <aug-spinner size="4" />
        <p>loading repositories</p>
      </div>
      <div class="groups" v-if="isLoaded">
        <repo-group
          v-for="rg in getRepoGroups"
          :key="rg.repo_group_id"
          :repoGroup="rg"
          ref="repoGroups"
          @dropdownclick="dropdownClick()"
        />
      </div>
    </div>
  </div>
</template>

<script>
import RepoGroup from "../../components/RepoGroup/RepoGroup.vue";
import ManageButtons from "./ManageButtons.vue";
import AugSpinner from "../../components/BaseComponents/AugSpinner.vue";
import DashboardHeader from "../Dashboard/dashboardHeader/DashboardHeader.vue";

import { mapGetters } from "vuex";

export default {
  name: "ManageRepos",
  components: {
    RepoGroup,
    ManageButtons,
    AugSpinner,
    DashboardHeader
  },
  methods: {
    collapseAll() {
      this.$refs.repoGroups.forEach(rg => rg.collapse());
    },
    dropdownClick() {
      this.$refs.repoGroups.forEach(rg => {
        rg.$refs.header.$refs.dropdown.collapse();
      });
    }
  },
  beforeCreate() {
    this.$store.dispatch("reposModule/retrieveRepoGroups", true);
    this.$store.dispatch("reposModule/retrieveRepos", true);
  },
  computed: {
    ...mapGetters("reposModule", [
      "isLoaded",
      "isGroupsLoaded",
      "getRepoGroups"
    ])
  }
};
</script>

<style scoped>
#ManageRepos {
  padding-bottom: 2rem;
}

#manage-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 3rem;
}

.groups {
  width: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.loading {
  margin-top: 4rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
}

.loading > p {
  color: var(--dark-grey);
}
</style>
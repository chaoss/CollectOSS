<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="RepoGroup" :class="{ open : !isCollapsed }">
    <repo-group-header ref="header" :repoGroup="repoGroup" :isCollapsed="isCollapsed" @flipCollapse="flipCollapse" @dropdownclick="$emit('dropdownclick')"/>
    <transition name="ease">
      <repo-group-content
        :repoGroup="repoGroup"
        :isCollapsed="isCollapsed"
        v-if="!isCollapsed"
      />
    </transition>
  </div>
</template>

<script>
import RepoGroupHeader from "./RepoGroupHeader.vue";
import RepoGroupContent from "./RepoGroupContent.vue";
import { mapGetters } from "vuex";

export default {
  name: "RepoGroup",
  components: {
    RepoGroupHeader,
    RepoGroupContent
  },
  props: {
    repoGroup: {
      type: Object,
      default: () => {
        return {
          rg_name: "sample repo group",
          repo_group_id: "sample rg_id"
        };
      }
    }
  },
  data() {
    return {
      isCollapsed: true,
      urlsInput: "",
      isCurrentlyAddingRepos: false
    };
  },
  computed: {
    ...mapGetters("reposModule", ["getReposInGroup"])
  },
  methods: {
    flipCollapse() {
      this.isCollapsed = !this.isCollapsed;
    },
    collapse() {
      this.isCollapsed = true;
    },
    open() {
      this.isCollapsed = false;
    }
  }
};
</script>

<style scoped>
#RepoGroup {
  background-color: white;
  width: 90%;
  max-width: 1200px;
  padding: .5rem;
  margin-top: 1rem;
  box-shadow: 5px 5px 20px 0 var(--grey);
  transition: background-color .1s;
}

#RepoGroup:hover {
  background-color: var(--light-grey);
  cursor: pointer;
}

.open {
  background-color: var(--light-grey) !important;
}
</style>
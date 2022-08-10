<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="RepoGroupHeader">
    <h1>{{ repoGroup.rg_name }}</h1>
    <div class="buttons">
      <aug-menu-dropdown
        :menuOptions="[ { key: 'deleteRepoGroup', text: 'delete repo group' }, { key: 'changeGroupName', text: 'change group name' } ]"
        @deleteRepoGroup="deleteGroup()"
        @changeGroupName="changeGroupName()"
      />
      <img
        src="https://img.icons8.com/material/24/000000/circled-chevron-up--v1.png"
        v-if="!isCollapsed"
        @click="$emit('flipCollapse')"
      />
      <img
        src="https://img.icons8.com/material/24/000000/circled-chevron-down--v1.png"
        v-if="isCollapsed"
        @click="$emit('flipCollapse')"
      />
    </div>
  </div>
</template>

<script>
import AugMenuDropdown from "../../../BaseComponents/AugMenuDropdown.vue";

export default {
  name: "RepoGroupHeader",
  components: {
    AugMenuDropdown
  },
  props: {
    repoGroup: {
      type: Object,
      default: () => {
        return {
          rg_name: "sample group",
          repo_group_id: "sampleid"
        };
      }
    },
    isCollapsed: {
      type: Boolean,
      default: true
    }
  }, 
  methods: {
    deleteGroup() {
      console.log('delete');
    }, 
    changeGroupName() {
      console.log('change name');
    }
  }
};
</script>

<style scoped>
#RepoGroupHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.buttons {
  align-items: center;
  display: flex;
  justify-content: space-evenly;
}

.buttons > * {
  margin-right: 1rem;
}

h1 {
  margin: 0rem;
  padding: 0.5rem;
  font-size: 1.5rem;
}

img {
  padding: 0.4rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 1.65rem;
  transition: background-color 0.2s ease;
}
</style>
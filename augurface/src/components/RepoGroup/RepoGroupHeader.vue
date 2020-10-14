<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="RepoGroupHeader">
    <h1>{{ repoGroup.rg_name }} ({{repoCountInGroup(repoGroup.repo_group_id)}})</h1>
    <div class="buttons">
      <!-- <aug-menu-dropdown
        :menuOptions="[ { key: 'deleteRepoGroup', text: 'delete repo group' }, { key: 'changeGroupName', text: 'change group name' } ]"
        @deleteRepoGroup="deleteGroup()"
        @changeGroupName="changeGroupName()"
        @click="$emit('dropdownclick')"
        ref="dropdown"
      /> -->
      <aug-icon-button iconClass="fas fa-arrow-up" v-if="!isCollapsed" @click="$emit('flipCollapse')" :class="{ open: !isCollapsed }" :circular="true" />
      <aug-icon-button iconClass="fas fa-arrow-down" v-if="isCollapsed" @click="$emit('flipCollapse')" :circular="true" />
    </div>
  </div>
</template>

<script>
// import AugMenuDropdown from "../BaseComponents/AugMenuDropdown.vue";
import AugIconButton from "../BaseComponents/AugIconButton.vue";
import { mapGetters } from 'vuex';

export default {
  name: "RepoGroupHeader",
  components: {
    // AugMenuDropdown, 
    AugIconButton
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
  computed: {
    ...mapGetters("reposModule", ["repoCountInGroup"])
  }, 
  methods: {
    hello() {
      console.log('hello');
    }, 
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
  align-items: flex-start !important;
  display: flex;
  justify-content: space-evenly;
}

.buttons > * {
  margin-right: .5rem;
}

h1 {
  margin: 0rem;
  padding: 0.5rem;
  font-size: 1.5rem;
}

.open {
  background-color: var(--grey) !important;
}
</style>
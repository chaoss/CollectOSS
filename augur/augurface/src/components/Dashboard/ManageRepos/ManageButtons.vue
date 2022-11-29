<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="ManageButtons">
    <div class="row">
      <div class="column">
        <!-- import repos -->
        <aug-text-input
          inputName="organizationName"
          text="Import repos from organization"
          placeholder="organization name..."
          @valueUpdated="setOrgUsernameInput"
        />
        <aug-button text="Import" @click="importReposFromOrganization()" />
        <img
          v-if="isImporting"
          src="../../../assets/loading.gif"
          alt="adding repos..."
          style="width: 35px; transform: translateX(-15px);"
        />
      </div>
      <div class="column">
        <!-- refresh repos -->
        <aug-button text="Refresh" @click="refreshRepos()" />
      </div>
    </div>
    <div class="row">
      <div class="column">
        <!-- create group -->
        <aug-text-input
          inputName="groupName"
          text="Create new repo group"
          placeholder="repo group name..."
          @valueUpdated="setGroupNameInput"
        />
        <aug-button text="Create" @click="createGroup()" />
      </div>
      <div class="column">
        <!-- collapse repos -->
        <aug-button text="Collapse All" @click="$emit('collapseAll')" />
      </div>
    </div>
  </div>
</template>

<script>
import AugButton from "../../BaseComponents/AugButton.vue";
import AugTextInput from "../../BaseComponents/AugTextInput.vue";
import { mapGetters } from "vuex";
export default {
  name: "ManageButtons",
  components: {
    AugButton,
    AugTextInput
  },
  data() {
    return {
      groupNameInput: "",
      orgUsernameInput: "",
      isImporting: false,
      isCreating: false
    };
  },
  computed: {
    ...mapGetters("reposModule", ["isLoaded"]),
    isDisabled() {
      return !this.isLoaded || this.isImporting || this.isCreating;
    }
  },
  methods: {
    refreshRepos() {
      if (this.isDisabled) {
        console.log("disabled");
        return;
      }
      this.$store.commit("reposModule/setReposLoaded", false);
      this.$store.commit("reposModule/setGroupsLoaded", false);
      this.$store.dispatch("reposModule/retrieveRepoGroups", false);
      this.$store.dispatch("reposModule/retrieveRepos", false);
    },
    createGroup() {
      if (this.isDisabled) {
        console.log("disabled");
        return;
      }
      // fetch request
      // then -> commit new group to vuex
      window.alert("Coming soon!");
    },
    importReposFromOrganization() {
      if (this.isDisabled) {
        console.log("disabled");
        return;
      }
      this.isImporting = true;
      // fetch request
      // then -> commit new repos to vuex
      let requestObject = {
        group: this.orgUsernameInput
      };
      fetch(`${this.$store.state.utilModule.baseEndpointUrl}/add-repo-group`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestObject)
      })
        .then(res => {
          this.isImporting = false;

          if (res.status === 500) {
            console.log("Server error (possible invalid organization name)");
            window.alert('Possible invalid organization name entered. Import failed.');
            return null;
          } else {
            return res.json();
          }
        })
        .then(res => {
          if (res != null) {
            window.alert('successfully imported github organization');
            this.$store.commit("reposModule/addRepos", res.repo_records_created)
            this.$store.commit("reposModule/addGroup", { repo_group_id: res.group_id, rg_name: res.rg_name });
          }
        });
    },
    setGroupNameInput(newValue) {
      this.groupNameInput = newValue;
    },
    setOrgUsernameInput(newValue) {
      this.orgUsernameInput = newValue;
    }
  }
};
</script>

<style scoped>
#ManageButtons {
  width: 90%;
  max-width: 1200px;
  margin: 0;
  background-color: var(--light-grey);
  padding: 1rem;
  box-shadow: 0 0 20px 0 var(--grey);
}

button {
  background-color: white !important;
}

.row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 1rem;
}

.column {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
}

.column > * {
  margin-right: 2rem;
}
</style>
<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="ManageButtons">
    <div class="row">
      <div class="column">
        <!-- import repos -->
        <aug-text-input
          inputName="organizationName"
          text="Import repos from org (this will take a while)"
          placeholder="organization name..."
          @valueUpdated="setOrgUsernameInput"
          class="text-input"
        />
        <aug-button text="Import" @click="importReposFromOrganization()" />
        <aug-spinner size="2" v-if="isImporting" />
      </div>
      <div class="column">
        <!-- refresh repos -->
        <aug-button text="Refresh" @click="refreshRepos" />
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
          class="text-input"
        />
        <aug-button text="Create" @click="createGroup()" />
        <aug-spinner size="2" v-if="isCreating" />
      </div>
      <div class="column">
        <!-- collapse repos -->
        <aug-button text="Collapse All" @click="$emit('collapseAll')" />
      </div>
    </div>
  </div>
</template>

<script>
import AugButton from "../../components/BaseComponents/AugButton.vue";
import AugTextInput from "../../components/BaseComponents/AugTextInput.vue";
import AugSpinner from "../../components/BaseComponents/AugSpinner.vue";
import { mapGetters } from "vuex";
export default {
  name: "ManageButtons",
  components: {
    AugButton,
    AugTextInput,
    AugSpinner
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
      } else {
        this.$store.dispatch("reposModule/refreshRepos");
      }
    },
    createGroup() {
      if (this.isDisabled) {
        console.log("disabled");
      } 
      else {
        if (this.groupNameInput === "") {
          window.alert("invalid group name");
          return;
        }

        this.isCreating = true;
        this.$store
          .dispatch("reposModule/createGroup", this.groupNameInput)
          .then(() => {
            this.isCreating = false;
          });
      }
    },
    importReposFromOrganization() {
      if (this.isDisabled) {
        console.log("disabled");
      } 
      else {
        this.isImporting = true;
        this.$store
          .dispatch("reposModule/importGroup", this.orgUsernameInput)
          .then(() => {
            this.isImporting = false;
          });
      }
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

.text-input {
  width: 350px;
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
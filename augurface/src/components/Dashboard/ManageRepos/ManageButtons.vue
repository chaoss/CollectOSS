<template>
  <div id="ManageButtons">
    <div class="row">
      <div class="column">
        <aug-text-input
          inputName="organizationName"
          text="Add Repos from User/Organization"
          placeholder="organization/username..."
          @valueUpdated="setOrgUsernameInput"
        />
        <aug-button text="Add" @click="importReposFromOrganization()"/>
      </div>
      <div class="column">
        <aug-button text="Refresh" @click="refreshRepos()" />
      </div>
    </div>
    <div class="row">
      <div class="column">
        <aug-text-input
          inputName="groupName"
          text="New Repo Group"
          placeholder="repo group name..."
          @valueUpdated="setGroupNameInput"
        />
        <aug-button text="Create" @click="createGroup()"/>
      </div>
      <div class="column">
        <aug-button text="Collapse All" @click="$emit('collapseAll')" />
      </div>
    </div>
  </div>
</template>

<script>
import AugButton from "../../BaseComponents/AugButton.vue";
import AugTextInput from "../../BaseComponents/AugTextInput.vue";
export default {
  name: "ManageButtons",
  components: {
    AugButton,
    AugTextInput
  }, 
  data() {
    return {
      groupNameInput: "", 
      orgUsernameInput: ""
    }
  }, 
  methods: {
    refreshRepos() {
      this.$store.commit("reposModule/setReposLoaded", false);
      this.$store.commit("reposModule/setGroupsLoaded", false);
      this.$store.dispatch("reposModule/retrieveRepoGroups");
      this.$store.dispatch("reposModule/retrieveRepos");
    }, 
    createGroup() {
        // fetch request
        // then -> commit new group to vuex
    }, 
    importReposFromOrganization() {
        // fetch request
        // then -> commit new repos to vuex
        let requestObject = {
          group: this.orgUsernameInput
        };
        fetch(`http://localhost:5000/${this.$store.state.utilModule.baseEndpointUrl}/add-repo-group`, {
          method: 'POST', 
          headers: {
            'Content-Type': 'application/json'
          }, 
          body: JSON.stringify(requestObject)
        })
        .then(res => res.text())
        .then(res => console.log(res));
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

<style>
#ManageButtons {
  width: 90%;
  max-width: 1200px;
  /* display: flex; */
  /* justify-content: space-between; */
  /* align-items: flex-end; */
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
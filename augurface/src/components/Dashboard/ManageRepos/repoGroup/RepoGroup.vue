<template>
  <div id="RepoGroup" @click="flipCollapse()" :class="{ open : !isCollapsed }">
    <div id="repo-group-header">
      <h1>{{ repoGroupObject.rg_name }} ({{ repoGroupObject.repo_group_id }}) </h1>
      <div class="buttons">
        <img src="https://img.icons8.com/material-rounded/24/000000/menu-2.png" id="menu-button" />
        <img
          src="https://img.icons8.com/material/24/000000/circled-chevron-up--v1.png"
          v-if="!isCollapsed"
        />
        <img
          src="https://img.icons8.com/material/24/000000/circled-chevron-down--v1.png"
          v-if="isCollapsed"
        />
      </div>
    </div>
    <transition name="ease">
      <div id="repos" v-if="!isCollapsed" @click="stopEventPropagation($event)">
        <div id="add-repos-input">
          <aug-text-input text="add repos" placeholder="comma seperated git urls" inputName="urls" @valueUpdated="setUrlsInput"/>
          <aug-button text="add" @click="addRepos()"/>
        </div>
        <div class="repo-list">
          <repo v-for="repo in reposInGroup()" :key="repo.repo_id" :repo_name="repo.repo_name"/>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import AugTextInput from '../../../BaseComponents/AugTextInput.vue';
import AugButton from '../../../BaseComponents/AugButton.vue';
import Repo from './Repo.vue';

export default {
  name: "RepoGroup",
  components: {
    AugTextInput, 
    AugButton, 
    Repo
  }, 
  props: {
    repoGroupObject: {
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
      urlsInput: ''
    };
  },
  methods: {
    flipCollapse() {
      this.isCollapsed = !this.isCollapsed;
    }, 
    collapse() {
      this.isCollapsed = true;
    }, 
    stopEventPropagation(e) {
      e.stopPropagation();
    }, 
    setUrlsInput(val) {
      this.urlsInput = val;
    }, 
    addRepos() {
      let urls = this.urlsInput.split(',').map(url => url.trim());
      console.log(urls);
      // fetch request
      // then -> commit new repos to vuex
    }, 
    reposInGroup() {
      return this.$store.state.reposModule.repos.filter(repo => repo.repo_group_id === this.repoGroupObject.repo_group_id);
    }
  }
};
</script>

<style scoped>
#RepoGroup {
  background-color: white;
  width: 90%;
  max-width: 1200px;
  padding: 1rem;
  margin-top: 1rem;
  box-shadow: 5px 5px 20px 0 var(--grey);
}

#RepoGroup:hover {
  background-color: var(--light-grey);
  cursor: pointer;
}

h1,
p {
  padding: 0;
  margin: 0;
}

h1 {
    font-size: 1.5rem;
}

p {
    padding: 1rem;
    color: grey;
}

#repo-group-header {
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

#repos {
  position: relative;
  top: .3rem;
}

.ease-enter-active,
.ease-leave-active {
  transition: max-height 0.3s, padding-top .3s;
  height: auto;
  overflow: hidden;
}

.ease-enter,
.ease-leave-to {
  max-height: 0;
}

.ease-leave,
.ease-enter-to {
  max-height: 80vh;
}

p {
  height: 200px;
}

.open {
    background-color: var(--light-grey) !important;
}

#add-repos-input {
  width: 70%;
  justify-content: flex-start;
  display: flex;
  align-items: flex-end;
}

#add-repos-input > * {
  margin-right: 2rem;
}

#add-repos-input button {
  background-color: white;
}

.repo-list {
  margin-top: 1rem;
  border-bottom: 1px solid var(--grey);
}
</style>
<template>
  <div id="RepoGroup" @click="flipCollapse()" :class="{ open : !isCollapsed }">
    <div id="repo-group-header">
      <h1>{{ repoGroupObject.rg_name }} ({{ repoGroupObject.repo_group_id }})</h1>
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
          <aug-text-input
            text="Add repos to group"
            placeholder="comma seperated git urls"
            inputName="urls"
            @valueUpdated="setUrlsInput"
          />
          <aug-button text="add" @click="addRepos()" />
          <img v-if="isCurrentlyAddingRepos" src="../../../../assets/loading.gif" alt="adding repos..." style="width: 35px; transform: translateX(-15px);">
        </div>
        <div class="repo-list">
          <repo
            v-for="repo in getReposInGroup(repoGroupObject.repo_group_id)"
            :key="repo.repo_id"
            :repo="repo"
          />
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import AugTextInput from "../../../BaseComponents/AugTextInput.vue";
import AugButton from "../../../BaseComponents/AugButton.vue";
import Repo from "./Repo.vue";
import { mapGetters } from "vuex";

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
    }, 
    stopEventPropagation(e) {
      e.stopPropagation();    // keep events from propogating to parent components
    },
    setUrlsInput(val) {
      this.urlsInput = val;
    },
    addRepos() {
      if (this.isCurrentlyAddingRepos) {
        return;
      }

      this.isCurrentlyAddingRepos = true;

      // setup
      let urls = this.urlsInput.split(",").map(url => url.trim());
      let requestBody = {
        group: this.repoGroupObject.rg_name,
        repos: urls
      };

      // make request
      fetch(
        `${this.$store.state.utilModule.baseEndpointUrl}/add-repos`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(requestBody)
        }
      )
        .then(res => {
          console.log(`STATUS: ${res.status}`);
          if (res.status === 200) {
            return res.json();
          } else {
            return null;
          }
        })
        .then(res => {
          if (res) {
            // update state
            this.$store.commit('reposModule/addRepos', res.sucess);
            this.isCurrentlyAddingRepos = false;
          }
        });
    },
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
  top: 0.3rem;
}

.ease-enter-active,
.ease-leave-active {
  transition: max-height 0.3s, padding-top 0.3s, height .3s;
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
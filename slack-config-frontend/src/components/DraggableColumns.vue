<template>
  <div id="DraggableColumns">
    <div class="column">
      <h3>Host Repos</h3>
      <div class="column-controls">
        <aug-text-input
          placeholder="search host repos..."
          @valueUpdated="setHostSearch"
          class="search-input"
        />
        <aug-button text="Refresh" class="column-button" @click="refreshRepos(augurHost)" />
      </div>
      <div class="draggable-column">
        <aug-spinner v-if="isLoading" style="margin-top: 3rem" />
        <draggable :list="hostRepos" :group="{ name: 'repos', pull: 'clone', put: false }">
          <repo
            v-for="repo in hostRepos"
            :name="repo.url"
            :group="repo.rg_name"
            :key="repo.repo_id"
            v-show="hostSearchFilter(repo.url + repo.rg_name)"
            :deletable="false"
            :checkable="true"
          />
        </draggable>
      </div>
    </div>
    <div class="column">
      <h3>Tracked Repos</h3>
      <div class="column-controls">
        <aug-text-input
          placeholder="search tracked repos..."
          @valueUpdated="setTrackedSearch"
          class="search-input"
        />
        <aug-button text="Clear" class="column-button" @click="clearTrackedRepos" />
      </div>
      <draggable
        class="draggable-column"
        :list="trackedRepos"
        group="repos"
        @change="checkForDuplicate"
      >
        <repo
          v-for="repo in trackedRepos"
          :name="repo.url"
          :group="repo.rg_name"
          :key="repo.repo_id"
          v-show="trackedSearchFilter(repo.url + repo.rg_name)"
          :checkable="false"
          :deletable="true"
        />
      </draggable>
    </div>
  </div>
</template>

<script>
import draggable from "vuedraggable";
import Repo from "./Repo.vue";
import AugTextInput from "./BaseComponents/AugTextInput.vue";
import AugButton from "./BaseComponents/AugButton.vue";
import AugSpinner from "./BaseComponents/AugSpinner.vue";

export default {
  name: "DraggableColumns",
  components: {
    draggable,
    Repo,
    AugTextInput,
    AugButton,
    AugSpinner
  },
  props: ["initialTrackedRepos"],
  methods: {
    setHostSearch(newValue) {
      this.hostSearch = newValue;
    },
    setTrackedSearch(newValue) {
      this.trackedSearch = newValue;
    },
    checkForDuplicate() {
      this.trackedRepos = this.trackedRepos.filter(
        (repo, i, arr) =>
          arr.findIndex(r => {
            return r.repo_id === repo.repo_id;
          }) === i
      );
    },
    trackedSearchFilter(repoKey) {
      return repoKey.includes(this.trackedSearch);
    },
    hostSearchFilter(repoKey) {
      return repoKey.includes(this.hostSearch);
    },
    clearTrackedRepos() {
      this.trackedRepos = [];
    },
    refreshRepos(host) {
      this.augurHost = host;
      console.log(host);
      this.hostRepos = [];
      this.trackedRepos = [];
      this.isLoading = true;
      fetch(host + "/repos")
        .then(res => {
          if (res.status === 200) {
            return res.json();
          } else {
            this.isLoading = false;
            return null;
          }
        })
        .then(res => {
          if (res == null) {
            return;
          } else {
            console.log(res);
            this.hostRepos = res.map(repo => {
              return {
                url: repo.url,
                rg_name: repo.rg_name,
                repo_id: repo.repo_id
              };
            });
            // console.log(this);
            this.hostRepos.forEach(repo => {
              if (this.$props.initialTrackedRepos.includes(repo.url)) {
                console.log("match");
                this.trackedRepos.push(repo);
              }
            });
            this.isLoading = false;
          }
        });
    }
  },
  mounted() {
    // this.refreshRepos();
  },
  data() {
    return {
      hostSearch: "",
      trackedSearch: "",
      augurHost: "null", 
      isLoading: false,
      hostRepos: [],
      trackedRepos: []
    };
  }
};
</script>

<style scoped>
#DraggableColumns {
  width: 70vw;
  min-width: 800px;
  display: flex;
  border-radius: 2rem;
}

.column-controls {
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.column-button {
  width: 35%;
  margin-left: 5%;
}

h3 {
  margin-top: 0;
}

.column {
  padding: 1rem;
  width: 40%;
  margin-left: 3%;
}

.draggable-column {
  background-color: white;
  border: 1px solid grey;
  height: 600px;
  overflow: auto;
}

.search-input {
  width: 60%;
}
</style>
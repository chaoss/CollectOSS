<template>
  <div id="DraggableColumns">
    <div class="column">
      <h3>Host Repos</h3>
      <aug-text-input
        placeholder="search host repos..."
        @valueUpdated="setHostSearch"
        class="text-input"
      />
      <draggable
        class="draggable-column"
        :list="hostRepos"
        :group="{ name: 'repos', pull: 'clone', put: false }"
      >
        <repo
          v-for="repo in hostRepos"
          :name="repo.repoName"
          :group="repo.repoGroup"
          :key="repo.repoName + repo.repoGroup"
          v-show="hostSearchFilter(repo.repoName + repo.repoGroup)"
          :deletable="false"
          :checkable="true"
        />
      </draggable>
    </div>
    <div class="column">
      <h3>Tracked Repos</h3>
      <aug-text-input
        placeholder="search tracked repos..."
        @valueUpdated="setTrackedSearch"
        class="text-input"
      />
      <draggable
        class="draggable-column"
        :list="trackedRepos"
        group="repos"
        @change="checkForDuplicate"
      >
        <repo
          v-for="repo in trackedRepos"
          :name="repo.repoName"
          :group="repo.repoGroup"
          :key="repo.repoName + repo.repoGroup"
          v-show="trackedSearchFilter(repo.repoName + repo.repoGroup)"
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

export default {
  name: "DraggableColumns",
  components: {
    draggable,
    Repo,
    AugTextInput
  },
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
            return (
              r.repoName === repo.repoName && r.repoGroup === repo.repoGroup
            );
          }) === i
      );
    },
    trackedSearchFilter(repoKey) {
      return repoKey.includes(this.trackedSearch);
    }, 
    hostSearchFilter(repoKey) {
      return repoKey.includes(this.hostSearch);
    }
  },
  data() {
    return {
      hostSearch: "",
      trackedSearch: "",
      hostRepos: [
        {
          repoName: "repo1",
          repoGroup: "groupA"
        },
        {
          repoName: "repo2",
          repoGroup: "groupA"
        },
        {
          repoName: "repo3",
          repoGroup: "groupA"
        },
        {
          repoName: "repo4",
          repoGroup: "groupB"
        },
        {
          repoName: "repo5",
          repoGroup: "groupB"
        },
        {
          repoName: "repo6",
          repoGroup: "groupA"
        },
        {
          repoName: "repo7",
          repoGroup: "groupA"
        },
        {
          repoName: "repo8",
          repoGroup: "groupA"
        },
        {
          repoName: "repo9",
          repoGroup: "groupB"
        },
        {
          repoName: "repo10",
          repoGroup: "groupB"
        },
        {
          repoName: "repo11",
          repoGroup: "groupA"
        },
        {
          repoName: "repo12",
          repoGroup: "groupA"
        },
        {
          repoName: "repo13",
          repoGroup: "groupA"
        },
        {
          repoName: "repo14",
          repoGroup: "groupB"
        },
        {
          repoName: "repo15",
          repoGroup: "groupB"
        }
      ],
      trackedRepos: [
        {
          repoName: "repo5",
          repoGroup: "groupB"
        }
      ]
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

.text-input {
  width: 60%;
  margin-bottom: 1rem;
}
</style>
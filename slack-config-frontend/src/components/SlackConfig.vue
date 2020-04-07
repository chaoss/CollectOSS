<template>
  <div id="SlackConfig">
      <draggable-columns />
  </div>
</template>

<script>
import DraggableColumns from "./DraggableColumns.vue";

export default {
    name: "SlackConfig", 
    components: {
        DraggableColumns
    }, 
    data() {
        return {
            repos: [
                {
                    repoName: "repo1", 
                    repoGroup: "groupA"
                }, 
                {
                    repoName: "repo2", 
                    repoGroup: "groupA"
                }
            ], 
            trackedRepos: [
                {
                    repoName: "repo3", 
                    repoGroup: "groupB"
                }
            ]
        }
    }
}
</script>

<style scoped>
#SlackConfig {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    flex-wrap: wrap;
}

.draggable-column {
    border: 1px solid grey;
}
</style>
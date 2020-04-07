<template>
  <div id="SlackConfig">
      <draggable-columns ref="repoColumns"/>
        <tracking-options @save="save"/>
  </div>
</template>

<script>
import DraggableColumns from "./DraggableColumns.vue";
import TrackingOptions from "./TrackingOptions.vue";

export default {
    name: "SlackConfig", 
    components: {
        DraggableColumns, 
        TrackingOptions
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
    }, 
    methods: {
        save(trackingOptions) {
            let requestObject = {
                trackedRepos: this.$refs.repoColumns.trackedRepos, 
                trackingOptions: trackingOptions
            }
            console.log(requestObject);
        }
    }
}
</script>

<style scoped>
#SlackConfig {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    flex-wrap: wrap;
}
</style>
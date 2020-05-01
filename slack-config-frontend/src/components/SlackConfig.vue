<template>
  <div id="SlackConfig">
    <div class="heading-row">
      <div>
        <img src="../assets/auggie.png" alt />
        <h1>Auggie Configuration</h1>
      </div>
      <div>
          <aug-text-input text="" placeholder="Augur Host Url..." />
          <aug-button text="Apply" />
      </div>
    </div>
    <div class="slack-config-content">
      <draggable-columns ref="repoColumns" :repos="repos"/>
      <tracking-options @save="save" />
    </div>
  </div>
</template>

<script>
import DraggableColumns from "./DraggableColumns.vue";
import TrackingOptions from "./TrackingOptions.vue";
import AugTextInput from "./BaseComponents/AugTextInput.vue";
import AugButton from "./BaseComponents/AugButton.vue";

export default {
  name: "SlackConfig",
  components: {
    DraggableColumns,
    TrackingOptions, 
    AugTextInput, 
    AugButton
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
    };
  },
  methods: {
    save(trackingOptions) {
      let requestObject = {
        trackedRepos: this.$refs.repoColumns.trackedRepos,
        trackingOptions: trackingOptions
      };
      console.log(requestObject);
    }
  }, 
};
</script>

<style scoped>
.slack-config-content {
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  flex-wrap: wrap;
}

.heading-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--grey);
  background-color: white;
  box-shadow: 0 0 10px var(--grey);
  padding: 1rem;
}

.heading-row  img {
  width: 80px;
  box-shadow: 0 0 20px var(--grey);
  border-radius: 10px;
}

.heading-row  h1 {
  margin: 0;
  font-size: 3rem;
  margin-left: 1.5rem;
}

.heading-row > div {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-right: 2rem;
}

.heading-row > div > * {
    margin-right: 1rem;
}
</style>
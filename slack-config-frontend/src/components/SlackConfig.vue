<template>
  <div id="SlackConfig">
    <div class="heading-row">
      <div>
        <img src="../assets/auggie.png" alt class="auggie-logo" />
        <h1>Auggie Configuration</h1>
      </div>
      <div>
          <!-- <aug-text-input text="" placeholder="Augur Host Url..." />
          <aug-button text="Apply" /> -->
          <p>{{ teamName }}</p>
          <img :src="teamImage" alt="" class="team-logo"/>
      </div>
    </div>
    <div class="slack-config-content">
      <draggable-columns ref="repoColumns" :initialTrackedRepos="initialTrackedRepos" />
      <tracking-options
        @save="save"
        :initialTrackedInsights="initialTrackedInsights"
        :initialMaxMessages="initialMaxMessages"
      />
    </div>
  </div>
</template>

<script>
import DraggableColumns from "./DraggableColumns.vue";
import TrackingOptions from "./TrackingOptions.vue";

export default {
  name: "SlackConfig",
  props: [
    "initialMaxMessages",
    "initialTrackedInsights",
    "initialTrackedRepos",
    "email",
    "teamID",
    "teamName",
    "teamImage"
  ],
  components: {
    DraggableColumns,
    TrackingOptions
    // AugTextInput,
    // AugButton
  },
  mounted() {
    console.log(this.props);
    if (
      !this.$props.initialMaxMessages ||
      !this.$props.initialTrackedInsights ||
      !this.$props.email ||
      !this.$props.teamID ||
      !this.$props.teamName ||
      !this.$props.teamImage
    ) {
      this.$router.push("login");
    }
  },
  methods: {
    save(trackingOptions) {
      console.log(trackingOptions);
      let maxMessages = Number(trackingOptions.maxMessages);
      console.log(maxMessages);
      if (maxMessages < 1) {
        window.alert("invalid maximum messages");
        return;
      }
      let requestObject = {
        tracked: [],
        maxMessages: maxMessages,
        repos: []
      };
      if (trackingOptions.trackedInsights.commitCount) {
        requestObject.tracked.push("code-changes");
      }
      if (trackingOptions.trackedInsights.issueCount) {
        requestObject.tracked.push("issues-new");
      }
      if (trackingOptions.trackedInsights.pullRequestCount) {
        requestObject.tracked.push("reviews");
      }
      if (trackingOptions.trackedInsights.newContributors) {
        requestObject.tracked.push("contributors-new");
      }
      if (trackingOptions.trackedInsights.linesChanged) {
        requestObject.tracked.push("code-changes-lines");
      }
      this.$refs.repoColumns.trackedRepos.forEach(repo => {
        requestObject.repos.push(repo.repo_id);
      });
      console.log(requestObject);
    }
  }
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

.auggie-logo {
  width: 80px;
  box-shadow: 0 0 20px var(--grey);
  border-radius: 10px;
}

.heading-row h1 {
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

.team-logo {
  width: 50px !important;
  height: 50px;
  border-radius: 10px !important;
  border: 1px solid lightgrey;
}
</style>
<template>
  <div id="TrackingOptions">
    <div class="section">
      <h4>Track Insight Anomolies For:</h4>
      <div class="section-options">
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setCommitCount" ref="commitCountBox"/>
          <p>Commit Count</p>
        </div>
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setLinesChanged" ref="linesChangedBox"/>
          <p>Lines Changed</p>
        </div>
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setNewContributors" ref="newContributorsBox"/>
          <p>New Contributors</p>
        </div>
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setIssueCount" ref="issueCountBox"/>
          <p>Issue Count</p>
        </div>
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setPullRequestCount" ref="pullRequestBox"/>
          <p>Pull Request Count</p>
        </div>
      </div>
    </div>
    <div class="section frequency-section">
      <p>Max Messages Per Day: </p>
      <aug-text-input text="" placeholder="" class="frequency-text-input" @valueUpdated="setMaxMessages" :number="true" :initial="initialMaxMessages"/>
    </div>
    <aug-button text="Save" class="save-button" @click="$emit('save', trackingOptions)"/>
  </div>
</template>

<script>
import AugCheckbox from "./BaseComponents/AugCheckbox.vue";
import AugButton from "./BaseComponents/AugButton.vue";
import AugTextInput from "./BaseComponents/AugTextInput.vue";

export default {
  name: "TrackingOptions", 
  props: ["initialMaxMessages", "initialTrackedInsights"], 
  mounted() {
    if (this.$props.initialTrackedInsights.map(i => i.S).includes("code-changes")) {
      this.trackingOptions.trackedInsights.commitCount = true;
      this.$refs.commitCountBox.flipIsChecked();
    }
    if (this.$props.initialTrackedInsights.map(i => i.S).includes("code-changes-lines")) {
      this.trackingOptions.trackedInsights.linesChanged = true;
      this.$refs.linesChangedBox.flipIsChecked();
    }
    if (this.$props.initialTrackedInsights.map(i => i.S).includes("issues-new")) {
      this.trackingOptions.trackedInsights.issueCount = true;
      this.$refs.issueCountBox.flipIsChecked();
    }
    if (this.$props.initialTrackedInsights.map(i => i.S).includes("reviews")) {
      this.trackingOptions.trackedInsights.pullRequestCount = true;
      this.$refs.pullRequestBox.flipIsChecked();
    }
    if (this.$props.initialTrackedInsights.map(i => i.S).includes("contributors-new")) {
      this.trackingOptions.trackedInsights.newContributors = true;
      this.$refs.newContributorsBox.flipIsChecked();
    }
  }, 
  components: {
    AugCheckbox,
    AugButton, 
    AugTextInput
  }, 
  data() {
    return {
      trackingOptions: {
        trackedInsights: {
          commitCount: false, 
          linesChanged: false, 
          newContributors: false, 
          issueCount: false, 
          pullRequestCount: false
        }, 
        maxMessages: this.initialMaxMessages
      }
    }
  }, 
  methods: {
    setCommitCount(newValue) {
      this.trackingOptions.trackedInsights.commitCount = newValue;
    }, 
    setLinesChanged(newValue) {
      this.trackingOptions.trackedInsights.linesChanged = newValue;
    }, 
    setNewContributors(newValue) {
      this.trackingOptions.trackedInsights.newContributors = newValue;
    }, 
    setIssueCount(newValue) {
      this.trackingOptions.trackedInsights.issueCount = newValue;
    }, 
    setPullRequestCount(newValue) {
      this.trackingOptions.trackedInsights.pullRequestCount = newValue;
    }, 
    setMaxMessages(newValue) {
      this.trackingOptions.maxMessages = newValue;
    }
  }
};
</script>

<style scoped>
#TrackingOptions {
  width: 27vw;
  margin-right: 2rem;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: flex-start;
  height: 700px;
}

#TrackingOptions > * {
  margin-top: 10rem;
}

.section-options {
  border: 1px solid var(--grey);
  padding: 1rem;
  display: flex;
  flex-direction: row;
  flex-wrap: wrap;
  background-color: white;
}

.checkbox-w-label {
  display: flex;
  align-items: center;
  width: 50%;
}

p {
  margin-left: 1rem;
}

h4 {
  margin: 0;
}

.frequency-text-input {
  width: 70px !important;
  margin-left: 1rem;
}

.frequency-section {
  display: flex;
  align-items: center;
  justify-content: flex-start;
}

.save-button {
  width: 100%;
}
</style>
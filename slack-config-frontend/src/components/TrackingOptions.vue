<template>
  <div id="TrackingOptions">
    <div class="section">
      <h4>Track Insights For:</h4>
      <div class="section-options">
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setCommitCount"/>
          <p>Commit Count</p>
        </div>
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setLinesAdded"/>
          <p>Lines Added</p>
        </div>
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setNewContributors"/>
          <p>New Contributors</p>
        </div>
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setNewIssues"/>
          <p>New Issues</p>
        </div>
        <div class="checkbox-w-label">
          <aug-checkbox @flipCheck="setPullRequests"/>
          <p>Pull Requests</p>
        </div>
      </div>
    </div>
    <div class="section frequency-section">
      <p>Notifications Per Day: </p>
      <aug-text-input text="" placeholder="..." class="frequency-text-input" @valueUpdated="setNotificationsPerDay"/>
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
          linesAdded: false, 
          newContributors: false, 
          newIssues: false, 
          pullRequests: false
        }, 
        notificationsPerDay: null
      }
    }
  }, 
  methods: {
    setCommitCount(newValue) {
      this.trackingOptions.trackedInsights.commitCount = newValue;
    }, 
    setLinesAdded(newValue) {
      this.trackingOptions.trackedInsights.linesAdded = newValue;
    }, 
    setNewContributors(newValue) {
      this.trackingOptions.trackedInsights.newContributors = newValue;
    }, 
    setNewIssues(newValue) {
      this.trackingOptions.trackedInsights.newIssues = newValue;
    }, 
    setPullRequests(newValue) {
      this.trackingOptions.trackedInsights.pullRequests = newValue;
    }, 
    setNotificationsPerDay(newValue) {
      this.trackingOptions.notificationsPerDay = newValue;
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
  width: 40px !important;
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
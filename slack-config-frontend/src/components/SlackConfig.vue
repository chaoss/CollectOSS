<template>
  <div id="SlackConfig">
    <div class="heading-row">
      <div>
        <img src="../assets/auggie.png" alt class="auggie-logo" />
        <h1>Auggie Configuration</h1>
      </div>
      <div>
          <aug-text-input text="" placeholder="Augur Host Url..." @valueUpdated="setHost" ref="hostInput"/>
          <aug-button text="Apply" @click="refreshRepos()"/>
          <!-- <p>{{ teamName }}</p>
          <img :src="teamImage" alt="" class="team-logo"/> -->
      </div>
    </div>
    <div class="slack-config-content">
      <draggable-columns ref="repoColumns" :initialTrackedRepos="initialTrackedRepos.map(r => r.S)" />
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
import AugTextInput from "./BaseComponents/AugTextInput.vue";
import AugButton from "./BaseComponents/AugButton.vue";

export default {
  name: "SlackConfig",
  props: [
    "initialMaxMessages",
    "initialTrackedInsights",
    "initialTrackedRepos",
    "email",
    "teamID",
    "host"
  ],
  components: {
    DraggableColumns,
    TrackingOptions, 
    AugTextInput,
    AugButton
  },
  mounted() {
    console.log(this.props);
    if (
      !this.$props.initialMaxMessages ||
      !this.$props.initialTrackedInsights ||
      !this.$props.email ||
      !this.$props.teamID || 
      !this.$props.host
    ) {
      this.$router.push("login");
    }
    if (this.augurHost === "null") {
      window.alert("It looks like this is your first time configuring Auggie, make sure to tell Auggie 'start tracking repositories' in your slack workspace and to specify your Augur url in the top right of this page.");
    }
    else {
      this.$refs.hostInput.value = this.augurHost
      this.$refs.repoColumns.refreshRepos(this.augurHost);
    }
  },
  data() {
    return {
      augurHost: this.host
    }
  }, 
  methods: {
    refreshRepos() {
      this.$refs.repoColumns.refreshRepos(this.augurHost)
    }, 
    setHost(newValue) {
      this.augurHost = newValue;
    }, 
    save(trackingOptions) {
      console.log(trackingOptions);
      let maxMessages = Number(trackingOptions.maxMessages);
      console.log(maxMessages);
      if (maxMessages < 1) {
        window.alert("invalid maximum messages");
        return;
      }
      let requestObject = {
        insightTypes: [],
        maxMessages: String(maxMessages),
        repos: [],
        groups: [],  
        host: this.augurHost, 
        email: this.email, 
        teamID: this.teamID
      };
      if (trackingOptions.trackedInsights.commitCount) {
        requestObject.insightTypes.push({"S": "code-changes"});
      }
      if (trackingOptions.trackedInsights.issueCount) {
        requestObject.insightTypes.push({"S": "issues-new"});
      }
      if (trackingOptions.trackedInsights.pullRequestCount) {
        requestObject.insightTypes.push({"S": "reviews"});
      }
      if (trackingOptions.trackedInsights.newContributors) {
        requestObject.insightTypes.push({"S": "contributors-new"});
      }
      if (trackingOptions.trackedInsights.linesChanged) {
        requestObject.insightTypes.push({"S": "code-changes-lines"});
      }
      this.$refs.repoColumns.trackedRepos.forEach(repo => {
        requestObject.repos.push({ "S": repo.url });
      });

      console.log(requestObject);

      fetch("http://localhost:5000/auggie/update_tracking", {
        method: "POST", 
        headers: {
          "Content-Type": "application/json"
        }, 
        body: JSON.stringify(requestObject)
      })
      .then(res => {
        if (res.status === 200) {
          window.alert("settings saved");
        } else {
          window.alert("unable to save settings");
        }
      });
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
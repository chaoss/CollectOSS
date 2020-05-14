<template>
  <div id="SlackConfig">
    <div class="heading-row">
      <div>
        <img src="../assets/auggie.png" alt class="auggie-logo" />
        <h1>Auggie Configuration</h1>
        <i class="far fa-question-circle fa-2x help" @click="showHelp()"></i>
      </div>
      <div>
        <aug-text-input
          text
          placeholder="Augur Host Url..."
          @valueUpdated="setHost"
          ref="hostInput"
          class="host-input"
        />
        <aug-button text="Apply" @click="refreshRepos()" />
        <!-- <p>{{ teamName }}</p>
        <img :src="teamImage" alt="" class="team-logo"/>-->
      </div>
    </div>
    <div class="slack-config-content">
      <draggable-columns
        ref="repoColumns"
        :initialTrackedRepos="initialTrackedRepos.map(r => r.S)"
      />
      <tracking-options
        @save="save"
        :initialTrackedInsights="initialTrackedInsights"
        :initialMaxMessages="initialMaxMessages"
      />
    </div>
    <div id="footer">
      <aug-button text="Logout" @click="logout()" />
      <div>
        <a href="http://augurlabs.io" target="_blank">Augur Labs</a> |
        <a href="https://github.com/augurlabs/auggie/issues" target="_blank">Report Issues</a>
      </div>
      <a
        target="_blank"
        href="https://slack.com/oauth/v2/authorize?client_id=370453254753.908657290918&scope=app_mentions:read,channels:read,chat:write,dnd:read,groups:read,im:history,im:read,im:write,reactions:read,reactions:write,team:read,users.profile:read,users:read,users:read.email,users:write&user_scope=im:read,im:write,team:read,users:read,users:read.email,chat:write"
      >
        <img
          alt="Add to Slack"
          height="40"
          width="139"
          src="https://platform.slack-edge.com/img/add_to_slack.png"
          srcset="https://platform.slack-edge.com/img/add_to_slack.png 1x, https://platform.slack-edge.com/img/add_to_slack@2x.png 2x"
          class="add-button"
        />
      </a>
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
      window.alert(
        "It looks like this is your first time configuring Auggie, Please follow these steps to set everything up. \n\n1) Click 'Add to Slack' on the bottom right of this page. \n2) tell Auggie in your Slack workspace to 'start tracking my repos'. \n3) Specify the url to your instance of Augur in the text-box in the top right corner of this page."
      );
    } else {
      this.$refs.hostInput.value = this.augurHost;
      this.$refs.repoColumns.refreshRepos(this.augurHost);
    }
  },
  data() {
    return {
      augurHost: this.host
    };
  },
  methods: {
    showHelp() {
      window.alert(
        "Please follow these steps to set Auggie up. \n\n1) Click 'Add to Slack' on the bottom right of this page. \n2) tell Auggie in your Slack workspace to 'start tracking my repos'. \n3) Specify the url to your instance of Augur in the text-box in the top right corner of this page."
      );
    },
    refreshRepos() {
      this.$refs.repoColumns.refreshRepos(this.augurHost);
    },
    setHost(newValue) {
      this.augurHost = newValue;
    },
    logout() {
      localStorage.removeItem("__auggie__cache");
      this.$router.push("login");
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
        requestObject.insightTypes.push({ S: "code-changes" });
      }
      if (trackingOptions.trackedInsights.issueCount) {
        requestObject.insightTypes.push({ S: "issues-new" });
      }
      if (trackingOptions.trackedInsights.pullRequestCount) {
        requestObject.insightTypes.push({ S: "reviews" });
      }
      if (trackingOptions.trackedInsights.newContributors) {
        requestObject.insightTypes.push({ S: "contributors-new" });
      }
      if (trackingOptions.trackedInsights.linesChanged) {
        requestObject.insightTypes.push({ S: "code-changes-lines" });
      }
      this.$refs.repoColumns.trackedRepos.forEach(repo => {
        requestObject.repos.push({ S: repo.url });
      });

      console.log(requestObject);

      fetch("http://auggie.augurlabs.io:5446/auggie/update_tracking", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestObject)
      }).then(res => {
        if (res.status === 200) {
          localStorage.setItem(
            "__auggie__cache",
            JSON.stringify({
              teamID: requestObject.teamID,
              email: requestObject.email,
              maxMessages: Number(trackingOptions.maxMessages),
              trackedRepos: requestObject.repos,
              trackedInsights: requestObject.insightTypes,
              host: requestObject.host
            })
          );
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

.add-button {
  border-radius: 5px;
  transition: box-shadow 0.3s ease;
}

.add-button:hover {
  box-shadow: 0 0 5px grey;
}

.help {
  color: var(--light-blue);
  transition: text-shadow 0.3s ease;
  margin-left: 1rem;
}

.help:hover {
  text-shadow: 0 0 5px grey;
  cursor: pointer;
}

#footer {
  display: flex;
  justify-content: space-between;
  width: 95vw;
  margin: auto;
  margin-top: 1.5rem;
}

.host-input {
  width: 400px;
}
</style>

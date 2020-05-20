<template>
  <div id="SlackLogin">
    <img src="../assets/auggie.png" alt class="logo" />
    <h1>Auggie SlackBot Configuration</h1>
    <a
      href="https://slack.com/oauth/v2/authorize?user_scope=identity.basic,identity.email,identity.team&client_id=370453254753.908657290918&redirect_uri=http%3A%2F%2Fauggie.augurlabs.io"
      target="_blank"
    >
      <img src="https://api.slack.com/img/sign_in_with_slack.png" class="slack-button" />
    </a>
  </div>
</template>

<script>
export default {
  name: "SlackLogin",
  mounted() {
    // UNCOMMENT THIS IF YOU ARE DEVELOPING OUT OF PRODUCTION AND NEED TO ACCESS CONFIGURATION PAGE
    // localStorage.setItem("__auggie__cache", JSON.stringify({
    //   teamID: "123456", 
    //   email: "someone@gmail.com", 
    //   maxMessages: 6,
    //   trackedRepos: [], 
    //   trackedInsights: [], 
    //   host: "notarealurl" 
    // }));

    // check if user is already logged in
    let cachedData = JSON.parse(localStorage.getItem("__auggie__cache"));
    if (cachedData != null) {
      this.$router.push({
        name: "slack-config",
        params: {
          teamID: cachedData.teamID,
          email: cachedData.email,
          initialMaxMessages: cachedData.maxMessages,
          initialTrackedRepos: cachedData.trackedRepos,
          initialTrackedInsights: cachedData.trackedInsights,
          host: cachedData.host
        }
      });
    }
  }
};
</script>

<style scoped>
#SlackLogin {
  margin: auto;
  border-radius: 2rem;
  width: 90%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-start;
  margin-top: 6rem;
}

#SlackLogin > * {
  margin-top: 1rem;
}

.slack-button {
  transition: box-shadow 0.3s ease;
  border-radius: 7px;
}

.slack-button:hover {
  box-shadow: 0 0 5px var(--grey);
}

.logo {
  width: 200px;
  box-shadow: 0 0 10px var(--dark-grey);
  border-radius: 20px;
}
</style>

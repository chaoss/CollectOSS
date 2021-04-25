<template>
  <div id="SlackLogin">
    <!-- <aug-text-input
      inputName="instanceUrl"
      text="augur instance url"
      placeholder="..."
      class="text-input"
      @valueUpdated="setInstanceUrl"
    />
    <aug-text-input inputName="email" text="email" placeholder="..." class="text-input" @valueUpdated="setEmail"/>
    <aug-text-input inputName="teamId" text="Team ID" placeholder="..." class="text-input" @valueUpdated="setTeamId"/>
    <aug-button text="Submit" @click="submit" class="aug-button"/> -->
    <img src="../assets/auggie.png" alt="" class="logo">
    <h1>Auggie SlackBot Configuration</h1>
    <a href="https://slack.com/oauth/v2/authorize?user_scope=identity.basic,identity.email,identity.team&client_id=370453254753.908657290918&redirect_uri=http%3A%2F%2Flocalhost%3A8080" target="_blank"><img src="https://api.slack.com/img/sign_in_with_slack.png" class="slack-button"/></a>
  </div>
</template>

<script>
// import AugTextInput from "./BaseComponents/AugTextInput.vue";
// import AugButton from "./BaseComponents/AugButton.vue";

export default {
  name: "SlackLogin",
  components: {
    // AugTextInput, 
    // AugButton
  },
  data() {
    return {
      instanceUrl: "",
      email: "",
      teamId: ""
    };
  },
  methods: {
    setInstanceUrl(newValue) {
      this.instanceUrl = newValue;
    },
    setEmail(newValue) {
      this.email = newValue;
    },
    setTeamId(newValue) {
      this.teamId = newValue;
    }, 
    submit() {
        console.log("finna submit info");
        this.$emit("submit", {
            instanceUrl: this.instanceUrl, 
            email: this.email, 
            teamId: this.teamId
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

.text-input {
  width: 50%;
}

.aug-button {
    margin-top: 2rem !important;
}

.slack-button {
  transition: box-shadow .3s ease;
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
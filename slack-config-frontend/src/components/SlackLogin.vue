<template>
  <div id="SlackLogin">
    <aug-text-input
      inputName="instanceUrl"
      text="augur instance url"
      placeholder="..."
      class="text-input"
      @valueUpdated="setInstanceUrl"
    />
    <aug-text-input inputName="email" text="email" placeholder="..." class="text-input" @valueUpdated="setEmail"/>
    <aug-text-input inputName="teamId" text="Team ID" placeholder="..." class="text-input" @valueUpdated="setTeamId"/>
    <aug-button text="Submit" @click="submit" class="aug-button"/>
  </div>
</template>

<script>
import AugTextInput from "./BaseComponents/AugTextInput.vue";
import AugButton from "./BaseComponents/AugButton.vue";

export default {
  name: "SlackLogin",
  components: {
    AugTextInput, 
    AugButton
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
</style>
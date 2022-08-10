<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="SlackConfig">
    <div id="not-logged-in" v-if="!isLoggedIn">
      <img src="../../assets/slacklogo.png" alt="Slack" class="logo" />
      <p>Looks like you're not signed in with Slack</p>
      <p>Sign in to manage your tracked repositories</p>
      <img src="../../assets/slackbutton.png" class="button" alt="sign in with slack" @click="signInWithSlack" />
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from "vuex";

export default {
  name: "SlackCongig",
  methods: {
    ...mapActions("userModule", ["signInWithSlack"])
  },
  computed: {
    ...mapGetters("userModule", ["isLoggedIn"])
  }
};
</script>

<style>
#not-logged-in {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  padding: 2rem;
  background-color: var(--light-grey);
  width: 60%;
  margin: auto;
  margin-top: 5rem;
  border-radius: 1rem;
  min-width: 700px;
}

#not-logged-in > .button {
  width: 12rem;
  background-color: var(--grey);
  border-radius: 0.5rem;
  transition: box-shadow 0.3s ease;
}

#not-logged-in > .button:hover {
  cursor: pointer;
  box-shadow: 0 0 4px 0 var(--grey);
}

#not-logged-in > .logo {
    margin-bottom: 2rem;
    width: 400px;
    padding: 1rem;
}

#not-logged-in > p {
  margin-top: 0rem;
  font-size: 1.5rem;
  padding: 0;
}
</style>
<template>
  <div id="app">
    <h1>Auggie Configuration</h1>
    <slack-login @submit="setConnectionInfo" v-if="!loggedIn" />
    <slack-config v-if="loggedIn" />
  </div>
</template>

<script>
import SlackLogin from "./components/SlackLogin.vue";
import SlackConfig from "./components/SlackConfig.vue";

export default {
  name: 'App',
  components: {
    SlackLogin, 
    SlackConfig
  }, 
  data() {
    return {
      loggedIn: false, 
      connectionInfo: {
        instanceUrl: "http://localhost:5000", 
        email: "michaelwoodruffdev@gmail.com", 
        teamId: "augurlabs"
      }
    }
  }, 
  methods: {
    setConnectionInfo(info) {
      this.connectionInfo = info;
      this.loggedIn = true;
      fetch(`${this.connectionInfo.instanceUrl}/api/unstable/auggie/get_user`, {
        method: "POST", 
        headers: {
          'Content-Type': 'application/json'
        }, 
        body: JSON.stringify({
          email: this.connectionInfo.email, 
          teamID: this.connectionInfo.teamId
        })
      })
      .then(res => {
        console.log(res.status);
        return res.json();
      })
      .then(res => {
        console.log(res);
      });
    }
  }, 
  mounted() {
    console.log("mounted");
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>

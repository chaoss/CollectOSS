<template>
  <div id="Auth">
    <p style="margin-top: 6rem">authenticating...</p>
  </div>
</template>

<script>
export default {
  name: "Auth",
  mounted() {
    let parameters = {};
    let parts = window.location.href.replace(
      /[?&]+([^=&]+)=([^&]*)/gi,
      function(m, key, value) {
        parameters[key] = value;
      }
    );
    console.log(parts);
    console.log(parameters);
    let code = parameters["code"];
    if (!code) {
      this.$router.push({
        name: "slack-config",
        params: {
          hello: "world",
          initialTrackedRepos: [
            "github.com/michaelwoodruffdev/PixelSmash.git"
          ], 
          initialMaxMessages: "4", 
          initialTrackedInsights: [
            "code-changes", 
            "reviews", 
            "code-changes-lines", 
            "contributors-new", 
            "issues-new"
          ], 
          teamName: "Augur Labs", 
          teamImage: "https://avatars.slack-edge.com/2018-05-27/371894580262_c09a2e5b16b9dd464b15_original.png", 
          teamID: "TAWDB7GN5", 
          email: "michaelwoodruffdev@gmail.com"
        }
      });
      // this.$router.push("login");
      return;
    }
    let requestObject = {
      code
    };
    fetch("http://localhost:5000/auggie/slack_login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(requestObject)
    }).then(res => {
      console.log(res);
      this.$router.push({
        name: "slack-config",
        params: {
          hello: "world",
          initialTrackedRepos: [
            "https://github.com/michaelwoodruffdev/PixelSmash.git"
          ]
        }
      });
      return null; // this is where I'll add logic for sending user info to configure page
      // console.log(res);
      // return res.json();
    });
    // .then(res => {
    //   // console.log(res);
    // });
  }
};
</script>

<style>
</style>
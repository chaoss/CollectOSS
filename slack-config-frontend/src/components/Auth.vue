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
      // this.$router.push({
      //   name: "slack-config",
      //   params: {
      //     hello: "world",
      //     initialTrackedRepos: [
      //       "github.com/michaelwoodruffdev/PixelSmash.git"
      //     ], 
      //     initialMaxMessages: "4", 
      //     initialTrackedInsights: [
      //       "code-changes", 
      //       "reviews", 
      //       "code-changes-lines", 
      //       "contributors-new", 
      //       "issues-new"
      //     ], 
      //     teamName: "Augur Labs", 
      //     teamImage: "https://avatars.slack-edge.com/2018-05-27/371894580262_c09a2e5b16b9dd464b15_original.png", 
      //     teamID: "TAWDB7GN5", 
      //     email: "michaelwoodruffdev@gmail.com"
      //   }
      // });
      this.$router.push("login");
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
      if (res.status === 200) {
        return res.json();
      } else {
        return null;
      }
      // this.$router.push({
      //   name: "slack-config",
      //   params: {
      //     hello: "world",
      //     initialTrackedRepos: [
      //       "https://github.com/michaelwoodruffdev/PixelSmash.git"
      //     ]
      //   }
      // });
      // console.log(res);
      // return res.json();
    })
    .then(res => {
      res = JSON.parse(res);
      console.log(typeof(res))
      console.log(res);
      this.$router.push({
        name: "slack-config", 
        params: {
          teamID: res.team_id, 
          email: res.email, 
          initialMaxMessages: res.user.maxMessages.N, 
          initialTrackedRepos: res.user.interestedRepos.L, 
          initialTrackedInsights: res.user.interestedInsights.L, 
          host: res.user.host.S
        }
      })
    });
  }
};
</script>

<style>
</style>
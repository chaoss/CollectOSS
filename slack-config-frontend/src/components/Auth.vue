<template>
  <div id="Auth">spinner</div>
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
    });
  }
};
</script>

<style>
</style>
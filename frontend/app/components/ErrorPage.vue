<template>
<div class="limiter">
  <router-link to="/"><img src="static/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/></router-link>
  <div class="container-login background"> <!-- background image -->
      <h1>Page Not Found</h1>
  </div>
</div>
</template>

<script>
  module.exports = {
    data() {
      return {
        'formAction': '/login?next=' + encodeURI('http://' + window.location.host)
      }
    },
    methods: {

    },
    computed: {

    }
  }

</script>

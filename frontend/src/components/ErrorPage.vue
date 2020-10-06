<!-- #SPDX-License-Identifier: MIT -->
<template>
<div class="limiter">
  <router-link to="/"><img src="@/assets/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/></router-link>
  <div class="container-login background"> <!-- background image -->
      <h1>Page Not Found</h1>
  </div>
</div>
</template>

<script>
 export default {
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

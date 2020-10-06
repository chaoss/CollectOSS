<!-- #SPDX-License-Identifier: MIT -->
<template>
<div class="limiter">
  <router-link to="/"><img src="@/assets/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/></router-link>
  <div class="container-login background"> <!-- background image -->
    <div class="wrap-login">
      <form class="login-form validate-form" :action="formAction" method="post">
        <div class="wrap-input validate-input" data-validate="Enter username">
          <input class="input" type="text" name="username" placeholder="Username">
        </div>

        <div class="wrap-input validate-input" data-validate="Enter password">
          <input class="input" type="password" name="password" placeholder="Password">
        </div>

        <div class="contact-form-checkbox">
          <input class="input-checkbox" id="ckb1" type="checkbox">
          <label class="label-checkbox" for="ckb1">
            Remember me
          </label>
        </div>

        <div class="container-login-form-btn">
          <input type="submit" class="login-form-btn" value="Login" />
        </div>

      </form>
    </div>
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

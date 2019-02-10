<template>
<div class="limiter">
  <!-- <div class="background"></div> -->
  <div class="container-login background"> <!-- background image -->
    <div class="wrap-login">
      <form class="login-form validate-form" :action="formAction" method="post">
        <div style="text-align: center; padding-right: 10px">
          <img src="static/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/>

        </div>

        <span class="login-form-title">
          Log in
        </span>

        <div class="wrap-input validate-input" data-validate="Enter username">
          <input class="input" type="text" name="username" placeholder="Username">
          <span class="focus-input" style="padding: 12px 0px 0px 10px">&#128100</span>
        </div>

        <div class="wrap-input validate-input" data-validate="Enter password">
          <input class="input" type="password" name="password" placeholder="Password">
          <span class="focus-input" style="padding: 12px 0px 0px 10px">&#128274</span>
        </div>

        <div class="contact-form-checkbox">
          <input class="input-checkbox" id="ckb1" type="checkbox">
          <label class="label-checkbox" for="ckb1">
            Remember me
          </label>
        </div>

        <div class="container-login-form-btn">
          <input type="submit" class="login-form-btn" name="submit">
            Login
          </input>
        </div>

      </form>
    </div>
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

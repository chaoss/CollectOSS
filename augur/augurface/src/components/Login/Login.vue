<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="Login">
    <login-card />
    <p class="link" v-on:click="$router.push('/create-account')">Create Account</p>
  </div>
</template>

<script>
import LoginCard from './LoginCard.vue';

export default {
  name: "Login", 
  components: {
    LoginCard
  }
};
</script>

<style>
.link {
    color: #0188EC;
    width: 150px;
    text-align: center;
    margin: auto;
    /* text-align: center; */
    font-size: 1.2rem;
    cursor: pointer;
    margin-top: 15px;
}

.link:hover {
    text-decoration: underline;
}
</style>
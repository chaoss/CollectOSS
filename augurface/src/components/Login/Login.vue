<template>
  <div id="Login">
    <!-- <div class="login-card">
      <img src="../assets/logo.png" alt />
      <div class="input-container username">
        <label for="username">Username:</label>
        <input type="text" name="username" id="input" />
      </div>
      <div class="input-container">
        <label for="password">Password:</label>
        <input type="password" name="password" id="input" />
      </div>
      <button>Login</button>
    </div> -->
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
.login-card {
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  align-items: center;
  background-color: white;
  width: 90%;
  max-width: 500px;
  margin: auto;
  margin-top: 8vh;
  border-radius: 4px;
  /* height: 90vh; */
  /* max-height: 500px; */
  box-shadow: 0px 0px 20px #cdcdcd;
}

.login-card > * {
    margin-top: 2.2rem;
}

.login-card > img {
  width: 90%;
  /* border-bottom: 1px solid #cdcdcd; */
  /* box-shadow: 0 10px 10px -15px black; */
  user-select: none;
}

.login-card > 

.login-card > .input-container {
    width: 80%;
    max-width: 300px;
}

.login-card > .input-container > input {
    margin: auto;
    width: 95%;
}

.login-card > .input-container > label {
    display: block;
    font-weight: 100;
}

.login-card > .username {
    margin-top: 1rem;
}

.login-card > button {
    padding: .3rem 4rem;
    /* background-image: linear-gradient(to bottom right, #0188EC, rgb(46, 163, 253)); */
    background-color: #efefef;
    border: 1px solid #b5b5b5;
    border-radius: 4px;
    margin-bottom: 2rem;
    font-size: 1.3rem;
    color: #232323;
    font-weight: 100;
    transition: border .2s ease, color .2s ease;
}

.login-card > button:hover {
    border: 1px solid #0188EC;
    color: #0188EC;
    cursor: pointer;
}

a {
    width: 100%;
    text-align: center;
    background-color: black;
}

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
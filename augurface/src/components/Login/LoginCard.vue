<template>
  <div class="login-card">
    <img src="../../assets/logo.png" alt />
    <div class="input-container username">
      <label for="username">Username:</label>
      <input
        type="text"
        name="username"
        id="input"
        v-model="username"
        v-on:keydown="keyboardInputListener($event)"
      />
    </div>
    <div class="input-container">
      <label for="password">Password:</label>
      <input
        type="password"
        name="password"
        ref="passwordInput"
        id="input"
        v-model="password"
        v-on:keydown="keyboardInputListener($event)"
      />
    </div>
    <button v-on:click="$router.push('/dashboard')" ref="loginButton">Login</button>
  </div>
</template>

<script>
export default {
  name: "LoginCard",
  data() {
    return {
      username: "",
      password: ""
    };
  },
  methods: {
    keyboardInputListener(e) {
      if (e.key === "Enter") {
        switch (e.originalTarget.name) {
          case "username":
              this.$refs.passwordInput.focus();
              break;
          case 'password':
              this.$refs.loginButton.click();
              break;
        }
      }
    }
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

img {
  width: 90%;
  /* border-bottom: 1px solid #cdcdcd; */
  /* box-shadow: 0 10px 10px -15px black; */
  user-select: none;
}

.input-container {
  width: 80%;
  max-width: 300px;
}

.input-container > input {
  margin: auto;
  width: 95%;
}

.input-container > label {
  display: block;
  font-weight: 100;
}

.username {
  margin-top: 1rem;
}

button {
  padding: 0.3rem 4rem;
  /* background-image: linear-gradient(to bottom right, #0188EC, rgb(46, 163, 253)); */
  background-color: #efefef;
  border: 1px solid #b5b5b5;
  border-radius: 4px;
  margin-bottom: 2rem;
  font-size: 1.3rem;
  color: #232323;
  font-weight: 100;
  transition: border 0.2s ease, color 0.2s ease;
}

button:hover {
  border: 1px solid #0188ec;
  color: #0188ec;
  cursor: pointer;
}
</style>
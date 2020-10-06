<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div class="login-card">
    <img src="../../assets/logo.png" alt />
    <aug-text-input
      text="Username"
      inputName="username"
      class="aug-input"
      @valueUpdated="setUsername"
    />
    <aug-text-input
      text="Password"
      inputName="password"
      class="aug-input"
      @valueUpdated="setPassword"
      :password="true"
    />
    <aug-button text="Login" @click="$router.push('/dashboard/manage')" ref="loginButton" />
  </div>
</template>




<script>
import AugButton from "../../components/BaseComponents/AugButton.vue";
import AugTextInput from "../../components/BaseComponents/AugTextInput.vue";

export default {
  data() {
    return {
      username: "",
      password: ""
    };
  },
  methods: {
    // listeners for keyboard presses during user input (specifically for 'Enter')
    keyboardInputListener(e) {
      if (e.key === "Enter") {
        switch (e.originalTarget.name) {
          case "username":
            this.$refs.passwordInput.focus();
            break;
          case "password":
            this.$refs.loginButton.$el.click();
            break;
        }
      }
    },
    setPassword(value) {
      this.password = value;
    },
    setUsername(value) {
      this.username = value;
    }
  },
  name: "LoginCard",
  components: {
    AugButton,
    AugTextInput
  }
};
</script>




<style scoped>
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
  box-shadow: 0px 0px 20px #cdcdcd;
  padding-bottom: 2rem;
}

.login-card > * {
  margin-top: 2.2rem;
}

.username {
  margin-top: 1rem;
}

img {
  width: 90%;
  user-select: none;
}

.aug-input {
  width: 80%;
  max-width: 300px;
}
</style>

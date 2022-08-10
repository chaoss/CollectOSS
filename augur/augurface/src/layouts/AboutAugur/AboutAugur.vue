<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="AboutAugur">
    <img src="../../assets/logo.png" alt="Augur" class="logo" />
    <p>Augur is software for storing and analyzing git repository metadata</p>
    <p style="margin-bottom: 2rem;">Check out our github page for more info</p>
    <aug-button
      text="Augur Github"
      @click="window.location.href = 'https://github.com/chaoss/augur'"
    />
  </div>
</template>

<script>
import AugButton from "../../components/BaseComponents/AugButton.vue";

export default {
  name: "AboutAugur",
  components: {
    AugButton
  }
};
</script>

<style scoped>
#AboutAugur {
  display: flex;
  flex-direction: column;
  margin: auto;
  align-items: center;
  margin-top: 2rem;
  background-color: var(--light-grey);
  margin: auto;
  width: 60%;
  min-width: 700px;
  margin-top: 5rem;
  border-radius: 1rem;
  padding: 2rem;
}

img {
  width: 400px;
}

p {
  margin-top: 0rem;
  font-size: 1.5rem;
  padding: 0;
}
</style>
<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="AboutAugur">
      <img src="../../../assets/logo.png" alt="Augur">
      <p>Augur is software for storing, managing and analyzing git repository metadata.</p>
      <p style="margin-bottom: 2rem;">Check out our github page for more information!</p>
      <aug-button text="Augur Github" @click="window.location.href = 'https://github.com/chaoss/augur'" />
  </div>
</template>

<script>
import AugButton from '../../BaseComponents/AugButton.vue';

export default {
    name: 'AboutAugur', 
    components: {
        AugButton
    }
}
</script>

<style scoped>
    #AboutAugur {
        display: flex;
        flex-direction: column;
        margin: auto;
        align-items: center;
        margin-top: 2rem;
    }

    img {
        width: 500px;
    }
</style>
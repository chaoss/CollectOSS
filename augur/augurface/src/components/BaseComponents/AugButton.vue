<!-- #SPDX-License-Identifier: MIT -->
<template>
  <button v-on:click="$emit('click')">{{ text }}</button>
</template>

<script>
export default {
    name: 'AugButton', 
    props: {
      text: {
        type: String, 
        required: false
      }
    }
};
</script>

<style scoped>
button {
  padding: 0.3rem 4rem;
  background-color: var(--light-grey);
  border: 1px solid var(--grey);
  border-radius: 4px;
  font-size: 1.3rem;
  color: var(--dark-grey);
  font-weight: 100;
  transition: border 0.2s ease, color 0.2s ease;
}

button:hover {
  border: 1px solid var(--light-blue);
  color: var(--light-blue);
  cursor: pointer;
}
</style>
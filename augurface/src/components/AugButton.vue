<template>
  <button v-on:click="$emit('click')">{{ text }}</button>
</template>

<script>
export default {
    name: 'AugButton', 
    props: [
        'text'
    ]
};
</script>

<style>
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
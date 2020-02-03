<template>
  <div id="AugTextInput">
      <label :for="inputName">{{text}}</label>
      <input
        :name="inputName"
        v-model="value"
        v-on:keydown="$emit('keydown', $event)"
        :type="password ? 'password' : 'text'"
      />
  </div>
</template>

<script>
export default {
    data() {
        return {
            value: '', 
        }
    }, 
    props: [
        'text', 
        'inputName', 
        'password'
    ], 
    watch: {
        value(val) {
            this.$emit('valueUpdated', val);
        }
    }
};
</script>

<style scoped>
label {
    display: block;
}

input {
    width: 100%;
}
</style>
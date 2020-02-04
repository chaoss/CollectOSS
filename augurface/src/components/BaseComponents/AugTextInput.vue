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
    color: var(--dark-grey);
}

input {
    width: 100%;
    font-size: 1rem;
    padding: .4rem;
    border: 1px solid var(--grey);
    border-radius: 3px;
    transition: border .2s ease;
}

input:focus {
    border: 1px solid var(--light-blue);
}
</style>
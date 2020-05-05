<template>
  <div id="AugTextInput">
    <label :for="inputName">{{text}}</label>
    <input
      :name="inputName"
      v-model="value"
      v-on:keydown="$emit('keydown', $event)"
      :type="password ? 'password' : number ? 'number' : 'text'"
      :placeholder="placeholder"
    />
  </div>
</template>

<script>
export default {
  name: "AugTextInput",
  data() {
    return {
      value: this.initial
    };
  },
  props: ["text", "inputName", "password", "placeholder", "number", "initial"],
  watch: {
    value(val) {
      this.$emit("valueUpdated", val);
    }
  }
};
</script>

<style scoped>
#AugTextInput {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
}
label {
  display: block;
}
input {
  width: 100%;
  font-size: 1rem;
  padding: 0.4rem;
  border: 1px solid var(--grey);
  border-radius: 3px;
  transition: border 0.2s ease;
}
input:focus {
  border: 1px solid var(--light-blue);
}
</style>
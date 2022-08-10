<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="AugTextArea">
    <label :for="inputName">{{text}}</label>
    <textarea v-model="value" :name="inputName" cols="30" rows="10" :placeholder="placeholder"></textarea>
  </div>
</template>

<script>
export default {
  name: "AugTextArea",
  data() {
    return {
      value: ""
    };
  },
  props: ["text", "inputName", "placeholder"],
  watch: {
    value(val) {
      this.$emit("valueUpdated", val);
    }
  }
};
</script>

<style scoped>
#AugTextArea {
  display: flex !important;
  flex-direction: column !important;
  justify-content: flex-start;
  align-items: flex-start;
  max-width: 90%;
}

textarea {
  padding: .5rem;
  font-size: .8rem;
  border-radius: 5px;
  border: 1px solid var(--grey);
  max-width: 100%;
  max-height: 800px;
  min-width: 300px;
  width: 500px;
  height: 50px;
}

textarea:focus {
    border: 2px solid var(--light-blue);
}
</style>
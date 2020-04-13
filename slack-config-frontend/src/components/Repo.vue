<template>
  <div id="Repo" @click="flipCheckbox">
    <p>{{ name }} ({{ group }})</p>
    <div class="righthand-options">
      <aug-checkbox v-if="checkable" ref="checkbox"/>
    </div>
  </div>
</template>

<script>
import AugCheckbox from "./BaseComponents/AugCheckbox.vue";

export default {
  name: "Repo",
  props: ["name", "group", "id", "deletable", "checkable"],
  components: {
    AugCheckbox
  }, 
  methods: {
      flipCheckbox() {
          if (this.checkable) {
              this.$refs.checkbox.flipIsChecked();
          }
      }
  }
};
</script>

<style scoped>
#Repo {
  display: flex;
  justify-content: space-between;
  background-color: white;
  color: var(--light-blue);
  padding: 1rem;
  border-bottom: 1px solid var(--grey);
}

#Repo:hover {
  cursor: pointer;
  background-color: var(--light-grey);
}

p {
  margin: 0;
}
</style>
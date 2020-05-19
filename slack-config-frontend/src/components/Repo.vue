<template>
  <div id="Repo" @click="flipCheckbox">
    <p>{{ name }} ({{ group }})</p>
    <div class="righthand-options">
      <aug-checkbox v-if="checkable" ref="checkbox" @flipCheck="setIsChecked"/>
      <i class="fas fa-times delete" v-if="deletable" @click="$emit('delete', id)" />
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
  data() {
    return {
      isChecked: false
    }
  }, 
  methods: {
      flipCheckbox() {
          if (this.checkable) {
              this.$refs.checkbox.flipIsChecked();
          }
      }, 
      setIsChecked(newValue) {
        this.isChecked = newValue;
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

.delete {
  color: var(--light-red);
  font-size: 1.8rem;
  transition: text-shadow .3s ease, color .3s ease;
}

.delete:hover {
  color: var(--red);
  text-shadow: 0 0 3px grey;
  cursor: pointer;
}
</style>
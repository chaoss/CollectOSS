<template>
  <div id="Repo">
      <p>{{ name }} ({{ group }})</p>
      <aug-checkbox />
  </div>
</template>

<script>
import AugCheckbox from "./BaseComponents/AugCheckbox.vue";

export default {
    name: "Repo", 
    props: ["name", "group", "id", "deletable"], 
    components: {
        AugCheckbox
    }
}
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
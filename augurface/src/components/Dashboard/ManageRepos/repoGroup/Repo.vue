<template>
  <div id="repo">
      {{ repo_name }}
  </div>
</template>

<script>
export default {
    name: 'repo', 
    props: {
        repo_name: {
            type: String, 
            required: true
        }
    }
}
</script>

<style scoped>
#repo {
    background-color: white;
    border-top: 1px solid var(--grey);
    padding: 1rem;
    color: var(--light-blue);
    font-size: 1.1rem;
}

#repo:hover {
    background-color: var(--light-grey);
    cursor: pointer;
    text-shadow: 1px 1px var(--grey);
}
</style>
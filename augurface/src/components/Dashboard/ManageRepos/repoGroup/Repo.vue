<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="repo">
      <p>{{ repo.url }}</p>
      <p>id: {{ repo.repo_id }}</p>
  </div>
</template>

<script>
export default {
    name: 'repo', 
    props: {
        repo: {
            type: Object, 
            required: true, 
            default: () => {
                return {
                    repo_id: '-1', 
                    repo_name: 'sample repo', 
                    description: 'sample description', 
                    repo_group_id: '-1', 
                    rg_name: 'sample group', 
                    url: 'sample/url/something.git'
                }
            }
        }
    }
}
</script>

<style scoped>
#repo {
    background-color: white;
    border: 1px solid var(--grey);
    border-bottom: 0;
    padding: 1rem;
    color: var(--light-blue);
    font-size: 1.1rem;
    display: flex;
    justify-content: space-between;
    width: 94%;
    margin: auto;
}

#repo:hover {
    background-color: var(--light-grey);
    cursor: pointer;
    text-shadow: 1px 1px var(--grey);
}

p {
    padding: .5rem;
    margin: 0;
}
</style>
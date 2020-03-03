<template>
  <div id="RepoGroupHeader">
      <h1>{{ repoGroup.rg_name }}</h1>
      <div class="buttons">
        <img src="https://img.icons8.com/material-rounded/24/000000/menu-2.png" id="menu-button" />
        <img
          src="https://img.icons8.com/material/24/000000/circled-chevron-up--v1.png"
          v-if="!isCollapsed"
        />
        <img
          src="https://img.icons8.com/material/24/000000/circled-chevron-down--v1.png"
          v-if="isCollapsed"
        />
      </div>
  </div>
</template>

<script>
export default {
    name: "RepoGroupHeader", 
    props: {
        repoGroup: {
            type: Object, 
            default: () => {
                return {
                    rg_name: "sample group", 
                    repo_group_id: "sampleid"
                }
            }
        }, 
        isCollapsed: {
            type: Boolean, 
            default: true
        }
    }
}
</script>

<style scoped>
#RepoGroupHeader {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.buttons {
  align-items: center;
  display: flex;
  justify-content: space-evenly;
}

.buttons > * {
  margin-right: 1rem;
}

h1 {
    margin: 0rem;
    padding: .5rem;
    font-size: 1.5rem;
}
</style>
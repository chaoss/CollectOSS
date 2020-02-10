<template>
  <div id="RepoGroup" @click="collapse()">
    <div id="repo-group-header">
      <h1>{{ repoGroupObject.rg_name }}</h1>
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
    <transition name="ease">
      <div id="repos" v-if="!isCollapsed">
        <p>id: {{ repoGroupObject.repo_group_id }}</p>
      </div>
    </transition>
  </div>
</template>

<script>
export default {
  name: "RepoGroup",
  props: {
    repoGroupObject: {
      type: Object,
      default: () => {
        return {
          rg_name: "sample repo group",
          repo_group_id: "sample rg_id"
        };
      }
    }
  },
  data() {
    return {
      isCollapsed: true
    };
  },
  methods: {
    collapse() {
      this.isCollapsed = !this.isCollapsed;
    }
  }
};
</script>

<style>
#RepoGroup {
  background-color: white;
  width: 90%;
  max-width: 1200px;
  padding: 1rem;
  margin-top: 1rem;
  box-shadow: 5px 5px 20px 0 var(--grey);
}

#RepoGroup:hover {
  background-color: var(--light-grey);
  cursor: pointer;
}

h1,
p {
  padding: 0;
  margin: 0;
}

#repo-group-header {
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

#repos {
  background-color: white;
  position: relative;
  top: .3rem;
}

.ease-enter-active,
.ease-leave-active {
  transition: max-height 0.3s, padding-top .3s;
  height: auto;
  overflow: hidden;
}

.ease-enter,
.ease-leave-to {
  max-height: 0;
}

.ease-leave,
.ease-enter-to {
  max-height: 400px;
}

p {
  height: 200px;
}
</style>
<template>
  <div id="NavBar">
      <div class="nav-links">
          <nav-link v-for="link in links" :key="link.path" v-bind="link" />
      </div>
      <img src="https://img.icons8.com/material-rounded/24/000000/menu-2.png" id="menu-button" />
  </div>
</template>

<script>
import NavLink from './NavLink.vue';

export default {
    name: 'NavBar', 
    props: {
        links: {
            type: Array, 
            required: false
        }
    }, 
    components: {
        NavLink
    }
}
</script>

<style scoped>
#NavBar {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

.nav-links {
  display: flex;
  width: 800px;
}

#menu-button {
  padding: .4rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 1.65rem;
  margin-right: 1rem;
  transition: background-color .2s ease;
}

#menu-button:hover {
    background-color: var(--light-grey);
    cursor: pointer;
}
</style>
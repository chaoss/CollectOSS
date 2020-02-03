<template>
  <header>
    <img src="../../assets/logo.png" alt />
    <div class="menu-bar">
      <div class="nav">
        <div class="nav-link" @click="$router.push('/dashboard/manage')">MANAGE REPOS</div>
        <div class="nav-link" @click="$router.push('/dashboard/analyze')">ANALYZE REPOS</div>
        <div class="nav-link" @click="$router.push('/dashboard/about')">ABOUT AUGUR</div>
      </div>
      <img src="https://img.icons8.com/material-rounded/24/000000/menu-2.png" id="menu-button" />
    </div>
  </header>
</template>

<script>
export default {
  name: "AugHeader", 
  data() {
      return {
      }
  }
};
</script>

<style scoped>
header {
  background-color: white;
  box-shadow: 0 0 20px 0 var(--grey);
  position: relative;
  overflow: visible;
}

.menu-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
}

img {
  width: 250px;
}

.nav {
  display: flex;
  position: sticky;
  top: 0;
}

.nav-link {
  font-size: 15px;
  padding: 0.7rem 0;
  text-align: center;
  width: 150px;
  background-color: white;
  font-weight: 300;
  color: var(-grey);
  transition: font-weight 0.2s ease, color 0.2s ease, background-color 0.2s ease;
}

.nav-link:hover {
  cursor: pointer;
  font-weight: 400;
  color: var(--dark-grey);
  background-color: var(--light-grey);
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
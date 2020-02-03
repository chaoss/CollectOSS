<template>
  <div id="Dashboard">
      <aug-header />
      <router-view />
  </div>
</template>

<script>
import AugHeader from './AugHeader.vue';

export default {
    name: "Dashboard", 
    components: {
        AugHeader
    }
};
</script>

<style>
#Dashboard {
    /* height: 150vh; */
}
</style>
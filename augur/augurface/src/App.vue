<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="app">
    <transition name="fade" mode="out-in">
      <router-view />
    </transition>
  </div>
</template>

<style>
#app {
  font-family: "Roboto";
}

.fade-enter-active, .fade-leave-active {
  transition: opacity .25s, transform .25s ease;
}

.fade-enter, .fade-leave-to {
  opacity: 0;
  transform: translateY(-100px);
}

.fade-enter-to, .fade-leave {
  opacity: 1;
  transform: translateY(0px);
}
</style>

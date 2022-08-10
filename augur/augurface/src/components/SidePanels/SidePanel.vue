<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="SettingsPanel">
    <slot></slot>
    <div id="darkenContainer" @click="$emit('darkClick')">
      <transition name="fadeFromBlack">
        <div id="darken" v-if="fade"></div>
      </transition>
    </div>
  </div>
</template>

<script>
export default {
  name: "SettingsPanel",
  data() {
    return {
      fade: false
    };
  },
  methods: {
    fadeOut() {
      this.fade = false;
    },
    fadeIn() {
      this.fade = true;
    }
  }
};
</script>

<style>
#SettingsPanel {
  background-color: var(--light-grey);
  border-left: 1px solid var(--grey);
  height: 100vh;
  width: 350px;
}

#darkenContainer {
    position: absolute;
    left: -120vw;
    width: 120vw;
    top: 0;
    height: 100vh;
    z-index: 1;
}

#darken {
  left: calc(-120vw);
  width: calc(120vw);
  background-color: #11111144;
  width: 100%;
  height: 100vh;
  z-index: 1;
}

.fadeFromBlack-enter-active,
.fadeFromBlack-leave-active {
  transition: opacity 0.3s ease, transform 0s;
}

.fadeFromBlack-enter,
.fadeFromBlack-leave-to {
  opacity: 0;
  transform: translateY(0);
}

.fadeFromBlack-enter-to,
.fadeFromBlack-leave {
  opacity: 1;
  transform: translateY(0);
}
</style>
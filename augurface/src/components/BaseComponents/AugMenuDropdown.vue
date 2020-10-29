<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="AugMenuDropdown" @click.stop>
    <aug-icon-button iconClass="fas fa-ellipsis-v" @click="flipCollapse" :class="{ open: !isCollapsed }" :circular="true"/>

    <div class="dropdown" v-if="!isCollapsed" v-click-outside="collapse">
      <div
        class="menuOption"
        v-for="option in menuOptions"
        :key="option.key"
        @click.stop="triggerOption(option.key)"
      >{{ option.text }}</div>
    </div>
  </div>
</template>

<script>
import ClickOutside from "vue-click-outside";
import AugIconButton from "./AugIconButton.vue";

export default {
  name: "AugMenuDropdown",
  props: {
    menuOptions: {
      type: Array,
      required: true,
      default() {
        return [{ key: "sampleKey", text: "sampleText" }];
      }
    }
  },
  data() {
    return {
      isCollapsed: true
    };
  },
  methods: {
    flipCollapse() {
      this.$emit('click');
      this.isCollapsed = !this.isCollapsed;
    },
    collapse() {
      this.isCollapsed = true;
    },
    triggerOption(optionKey) {
      this.$emit(optionKey);
    }
  },
  components: {
    AugIconButton
  }, 
  directives: {
    ClickOutside
  }
};
</script>

<style scoped>
#AugMenuDropdown {
  position: relative;
  top: 2px;
}

.dropdown {
  z-index: 4;
  background-color: white;
  position: absolute;
  bottom: -3rem;
  right: 1rem;
  border-radius: 3px;
  overflow: hidden;
  border: 1px solid var(--grey);
  border-top: none;
}

.menuOption {
  padding: 0.3rem 2rem;
  border-top: 1px solid var(--grey);
  white-space: nowrap;
}

.menuOption:hover {
  cursor: pointer;
  background-color: var(--light-grey);
  color: var(--light-blue);
}

.open {
  background-color: var(--grey) !important;
}
</style>
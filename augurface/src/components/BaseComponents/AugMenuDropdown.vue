<template>
  <div id="AugMenuDropdown" @click.stop>
    <img
      src="https://img.icons8.com/material-rounded/24/000000/menu-2.png"
      id="menu-button"
      @click.stop="flipCollapse"
      :class="{ open: !isCollapsed }"
    />
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
      this.isCollapsed = !this.isCollapsed;
    },
    collapse() {
      this.isCollapsed = true;
    },
    triggerOption(optionKey) {
      this.$emit(optionKey);
    }
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

img {
  padding: 0.4rem;
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 1.65rem;
  transition: background-color 0.2s ease;
}

img:hover {
  background-color: var(--grey);
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

.fade-enter-active {
  transition: opacity 0.2s ease;
}

.fade-enter,
.fade-leave-to {
  opacity: 0;
}

.fade-enter-to,
.fade-leave {
  opacity: 1;
}
</style>
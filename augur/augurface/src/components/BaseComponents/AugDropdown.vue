<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="AugDropdown" @click.stop>
    <label for="selected">
      <slot></slot>
    </label>
    <div id="dropdown">
      <div id="selected" @click="flipCollapse">
        {{ selectedValue.text }}
        <i class="fas fa-arrow-down"></i>
      </div>
      <div id="dropdown-options" v-if="!isCollapsed" v-click-outside="collapse">
        <div
          class="menuOption"
          v-for="option in options"
          :key="option.text"
          @click.stop="changeSelected(option)"
        >{{ option.text }}</div>
      </div>
    </div>
  </div>
</template>

<script>
import ClickOutside from "vue-click-outside";

export default {
  name: "AugDropdown",
  props: {
    options: {
      type: Array,
      required: true,
      default: () => {
        return [
          {
            text: "sample",
            value: "sample"
          },
          {
            text: "option",
            value: "option"
          }
        ];
      }
    },
    defaultOption: {
      type: Object,
      required: false
    }
  },
  data() {
    return {
      isCollapsed: true,
      selectedValue: { text: "sample", value: "sample" }
    };
  },
  mounted() {
    if (this.defaultOption != null) {
      this.selectedValue = this.defaultOption
    } else {
        this.selectedValue = this.options[0];
    }
  },
  directives: {
    ClickOutside
  },
  methods: {
    flipCollapse() {
      this.$emit("click");
      this.isCollapsed = !this.isCollapsed;
    },
    collapse() {
      this.isCollapsed = true;
    },
    changeSelected(option) {
      this.selectedValue = option;
      this.$emit("selectionChanged", option.value);
      this.collapse();
    }
  }
};
</script>

<style scoped>
#dropdown {
  min-width: 200px;
  background-color: white;
  border-radius: 0.2rem;
  border: 1px solid var(--grey);
}

#selected {
  padding: 0.5rem;
  display: flex;
  flex-direction: row;
  justify-content: space-between;
  align-items: center;
  font-weight: 900;
}

.dropdown-options {
  z-index: 4;
  background-color: white;
  position: absolute;
  bottom: -3rem;
  right: 1rem;
  border-radius: 3px;
  overflow: hidden;
  border-top: none;
}

.menuOption {
  padding: 0.3rem 0.6rem;
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
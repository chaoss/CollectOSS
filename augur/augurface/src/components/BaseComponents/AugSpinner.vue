<!-- #SPDX-License-Identifier: MIT -->
<template>
  <i class="fas fa-asterisk" ref="spinnerIcon"></i>
</template>

<script>
export default {
  name: "AugSpinner",
  props: {
    size: {
      type: String,
      required: false,
      default: () => {
        return "2";
      }
    }
  },
  data() {
    return {
      angle: 0,
      interval: null, 
      interval2: null
    };
  },
  mounted() {
    this.$refs.spinnerIcon.className += ` fa-${this.size}x`;
    this.$nextTick(() => {
      this.angle += 120;
      this.$refs.spinnerIcon.style.transform = `rotate(${this.angle}deg)`;
    });
    this.interval = setInterval(() => {
      this.angle += 240;
      this.$refs.spinnerIcon.style.transform = `rotate(${this.angle}deg)`;
    }, 400);
  },
  beforeDestroy() {
    clearInterval(this.interval);
    clearInterval(this.interval2);
  }
};
</script>

<style scoped>
i {
  transition: transform 0.6s ease;
  transform: rotate(0deg);
  color: var(--light-blue);
  transform-origin: center;
}
</style>
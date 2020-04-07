<template>
  <div id="AugCheckbox" @click="flipIsChecked" :class="{ checked: isChecked }">
      <i class="fas fa-check" :class="{ checkmarkChecked: isChecked }"></i>
  </div>
</template>

<script>
export default {
    name: "AugCheckbox", 
    data() {
        return {
            isChecked: false
        }
    }, 
    methods: {
        flipIsChecked() {
            this.isChecked = !this.isChecked;
            this.$emit("flipCheck", this.isChecked);
        }
    }
}
</script>

<style>
#AugCheckbox {
    border: 1px solid var(--grey);
    padding: .1rem .2rem;
}

i {
    color: #11111100;
}

.checked {
    background-color: var(--light-blue);
}

.checkmarkChecked {
    color: white;
}
</style>
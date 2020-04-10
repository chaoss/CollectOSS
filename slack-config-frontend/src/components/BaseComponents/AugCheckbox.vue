<template>
  <div id="AugCheckbox" @click.stop="flipIsChecked" :class="{ checked: isChecked }">
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
    max-width: 1rem;
    max-height: 1rem;
    padding: .2rem;
}

#AugCheckbox:hover {
    cursor: pointer;
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
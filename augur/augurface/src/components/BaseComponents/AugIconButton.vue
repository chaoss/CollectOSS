<!-- #SPDX-License-Identifier: MIT -->
<template>
    <div class="AugIconButton" @click="$emit('click', $event)" :class="{ circle: circular }">
      <i :class="iconClass"></i>
    </div>
</template>

<script>
export default {
    name: "AugIconButton", 
    props: {
        iconClass: {
            type: String, 
            required: true, 
            default: function () {
                return "fas fa-arrow-up"
            }
        }, 
        circular: {
            type: Boolean, 
            required: false, 
            default: function () {
                return false
            }
        }
    }
}
</script>

<style scoped>
.AugIconButton {
    width: 1.5rem;
    height: 1.5rem;
    display: flex;
    justify-content: center;
    align-items: center;
    padding: .5rem;
    transition: background-color .2s ease;
}

.AugIconButton:hover {
    background-color: var(--grey);
    cursor: pointer;
}

.circle {
    border-radius: 1.5rem !important;
}

</style>
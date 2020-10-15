<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div :class="classObject" @click="$router.push(path)">{{text}}</div>
</template>

<script>
export default {
    name: "NavLink", 
    props: {
        path: {
            type: String, 
            required: true
        }, 
        text: {
            type: String, 
            required: true
        }
    }, 
    data() {
        return {
            classObject: {
                NavLink: true, 
                selected: false
            }
        }
    }, 
    mounted() {
        // check if current route is selected on mounting
        if (this.$route.path.includes(this.path)) {
            this.classObject.selected = true;
        }
    }, 
    watch: {
        // toggle 'selected' class on route change
        '$route.path'(val) {
            if (val.includes(this.path)) {
                this.classObject.selected = true;
            } else {
                this.classObject.selected = false;
            }
        }
    }
}
</script>

<style scoped>
.NavLink {
  font-size: 15px;
  padding: 0.7rem 0;
  text-align: center;
  width: 150px;
  background-color: white;
  font-weight: 300;
  color: var(-grey);
  border-top: 2px solid #11111100;
  transition: font-weight 0.2s ease, color 0.2s ease, background-color 0.2s ease, border .2s ease, color .2s ease;
}

.NavLink:hover {
  cursor: pointer;
  font-weight: 400;
  color: var(--dark-grey);
  background-color: var(--light-grey);
}

.selected {
    color: var(--light-blue) !important;
    background-color: var(--light-grey);
    border-top: 2px solid var(--light-blue);
}
</style>
<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div id="SettingsPanel">
      <aug-dropdown class="dropdown" @selectionChanged="setBaseEndpointUrl" :options="getAvailableEndpointsForDropdown" :defaultOption="getCurrentEndpointUrlForDropdown">augur host</aug-dropdown>
  </div>
</template>

<script>
import AugDropdown from "../BaseComponents/AugDropdown.vue";
import { mapMutations, mapGetters } from "vuex";

export default {
    name: "SettingsPanel", 
    components: {
        AugDropdown
    }, 
    data() {
        return {

        }
    }, 
    methods: {
        ...mapMutations("utilModule", ["setBaseEndpointUrl"])
    }, 
    computed: {
        ...mapGetters("utilModule", ["getCurrentEndpointUrlForDropdown", "getAvailableEndpointsForDropdown"])
    }
}
</script>

<style scoped>
#SettingsPanel {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
}

#SettingsPanel > * {
    margin-top: 1rem;
}

.dropdown {
    width: 80% !important;
}
</style>
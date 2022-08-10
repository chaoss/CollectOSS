<!-- #SPDX-License-Identifier: MIT -->
<template>
  <header id="DashboardHeader">
    <img src="../../../assets/logo.png" alt />
    <div class="input-section">
      <!-- <aug-text-input text="Augur Host URL" placeholder="Augur Host URL (no trailing slash)..." ref="urlInput" /> -->
      <aug-text-input text="Database Key" placeholder="Key provided at database creation..." ref="keyInput" :password="true"/>
      <aug-button text="Apply" @click="apply"/>
    </div>
    <!-- <nav-bar :links="links"/> -->
  </header>
</template>

<script>
// import NavBar from "./NavBar.vue";
import AugTextInput from "../../../components/BaseComponents/AugTextInput.vue";
import AugButton from "../../../components/BaseComponents/AugButton.vue";
import { mapMutations, mapActions, mapGetters } from "vuex";

export default {
  name: "DashboardHeader",
  data() {
    return {
      links: [
        { text: "MANAGE REPOS", path: "/dashboard/manage" },
        // { text: "ANALYZE REPOS", path: "/dashboard/analyze" },
        { text: "CONFIGURE SLACK", path: "/dashboard/slack" }, 
        { text: "ABOUT AUGUR", path: "/dashboard/about" }
      ]
    };
  },
  components: {
    // NavBar 
    AugTextInput, 
    AugButton
  }, 
  methods: {
    apply() {
      // console.log(this.$refs.urlInput.value);
      // this.setBaseEndpointUrl(this.$refs.urlInput.value);
      this.setCrudKey(this.$refs.keyInput.value);
      alert("key updated");
      // this.refreshRepos();
    }, 
    ...mapMutations('utilModule', ['setBaseEndpointUrl', 'setCrudKey']), 
    ...mapActions('reposModule', ['refreshRepos'])
  }, 
  computed: {
    ...mapGetters('utilModule', ['getBaseEndpointUrl', 'getCrudKey'])
  }, 
  mounted() {
    // this.$refs.urlInput.value = this.getBaseEndpointUrl;
    this.$refs.keyInput.value = this.getCrudKey
    console.log(this.getCrudKey);
  }
};
</script>

<style scoped>
header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-right: 3rem;
  background-color: white;
  box-shadow: 0 0 20px 0 var(--grey);
  z-index: 10;
  position: sticky;
  top: 0;
}

img {
  width: 250px;
}

.input-section {
  display: flex;
  flex-direction: row;
  align-items: flex-end;
}
.input-section > * {
  margin-left: 2rem;
}

</style>
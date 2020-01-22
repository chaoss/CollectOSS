<template>
  <d-container fluid class="main-content-container px-4">
    
  </d-container>
</template>

<script lang="ts">
import {mapActions, mapGetters, mapMutations} from "vuex";
import Component from 'vue-class-component';
import Vue from 'vue';
import SlackSettingSync from "@/AugurAPI";

@Component({
  methods: {
    getUser: function(email, teamId) {
      //method will return user object with host, interestedRepos and interestedGroups
      SlackSettingSync.getUser(email, teamId);
    }
    updateTracking: function(email, teamId, repos, groups) {
      //method will return user object with host, interestedRepos and interestedGroups
      SlackSettingSync.updateTracking(email, teamId, repos, groups);
    }
  },
  computed: {

  },
  components: {

  }
})
export default class SlackConfig extends Vue {

}
</script>


<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div>
    <div class="fullwidth">
      <router-view name="header"></router-view>
      <!-- <augur-header></augur-header> -->
    </div>

    <div ref="cards" class="content">
      <router-view name="tabs"></router-view>

      <router-view name="controls"></router-view>

      <router-view name="content"></router-view>
    </div>
  </div>
</template>

<script>
import AugurHeader from "../components/AugurHeader.vue";
import MetricsStatusCard from "../components/MetricsStatusCard.vue";
import BaseRepoActivityCard from "../components/BaseRepoActivityCard.vue";
import BaseRepoEcosystemCard from "../components/BaseRepoEcosystemCard.vue";
import GrowthMaturityDeclineCard from "../components/GrowthMaturityDeclineCard";
import RiskCard from "../components/RiskCard";
import ValueCard from "../components/ValueCard";
import DiversityInclusionCard from "../components/DiversityInclusionCard";
import GitCard from "../components/GitCard";
import OverviewCard from "../components/OverviewCard.vue";
import ExperimentalCard from "../components/ExperimentalCard";
import DownloadedReposCard from "../components/DownloadedReposCard.vue";
import MainControls from "../components/MainControls.vue";
import LoginForm from "../components/LoginForm";
import { mapState } from "vuex";
export default {
  props: [
    "owner",
    "repo",
    "repoID",
    "repoGroupID",
    "domain",
    "comparedowner",
    "comparedrepo",
    "groupid"
  ],
  components: {
    MainControls,
    AugurHeader,
    MetricsStatusCard,
    BaseRepoActivityCard,
    BaseRepoEcosystemCard,
    GrowthMaturityDeclineCard,
    RiskCard,
    ValueCard,
    DiversityInclusionCard,
    GitCard,
    ExperimentalCard,
    DownloadedReposCard,
    LoginForm
  },

  watch: {
    $route: function(to, from) {
      if (to.path != from.path) window.location.reload();
      // window.location.replace(to.path)
    }
  },
  methods: {
    onRepo(e) {
      let repo = window.AugurAPI.Repo({
        githubURL: e.target.value
      });
      if (!repo.batch(["codeCommits"], true)[0]) {
        alert(
          "The repo " +
            repo.githubURL +
            " could not be found. Please try again."
        );
      } else {
        this.$store.commit("resetBaseRepo");
        this.$store.commit("setRepo", {
          githubURL: e.target.value
        });
        this.$router.push({
          name: "gmd",
          params: {
            owner: repo.owner,
            repo: repo.name,
            repoID: repo.repoID,
            repoGroupID: repo.repoGroupID
          }
        });
      }
    }
  }
};
</script>
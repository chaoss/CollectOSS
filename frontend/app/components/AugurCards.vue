<template>
  <div>

    <!-- content to show if app has no state yet -->
    <div :class="{ hidden: hasState }">
      <section class="unmaterialized">
        <div id="collapse">
          <h3 v-if="isCollapsed" @click="collapseText">Downloaded Git Repos by Project  <span style="font-size:16px">&#9660</span></h3>
          <h3 v-else @click="collapseText">Downloaded Git Repos by Project  <span style="font-size:16px">&#9654</span></h3>
        </div>
        <downloaded-repos-card></downloaded-repos-card>
      </section>

      <section class="unmaterialized">
        <all-metrics-status-card></all-metrics-status-card>
      </section>
    </div>

    <!-- content to show if app does have a repo to show -->
    <div :class="{ hidden: !hasState }">
      <nav class="tabs">
        <ul>
          <li :class="{ active: (currentTab == 'gmd'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="gmd">Growth, Maturity, and Decline</a></li>
          <li :class="{ active: (currentTab == 'diversityInclusion'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="diversityInclusion">Diversity and Inclusion</a></li>
          <li :class="{ active: (currentTab == 'risk'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="risk">Risk</a></li>
          <li :class="{ active: (currentTab == 'value'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="value">Value</a></li>
          <li :class="{ active: (currentTab == 'activity'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="activity">Activity</a></li>
          <li :class="{ active: (currentTab == 'experimental'), hidden: !baseRepo }"><a href="#" @click="changeTab" data-value="experimental">Experimental</a></li>
          <li :class="{ active: (currentTab == 'git'), hidden: !gitRepo }"><a href="#" @click="changeTab" data-value="git">Git</a></li>
        </ul>
      </nav>

      <div ref="cards">
        <main-controls></main-controls>
        <div v-if="(baseRepo && (currentTab == 'gmd'))">
          <growth-maturity-decline-card></growth-maturity-decline-card>
          <div id="comparisonCards" v-bind:class="{ hidden: !comparedRepos.length }" v-for="repo in comparedRepos">
            <compared-repo-growth-maturity-decline-card :comparedTo="repo"></compared-repo-growth-maturity-decline-card>
          </div>
        </div>
        <div v-if="(baseRepo && (currentTab == 'diversityInclusion'))">
          <diversity-inclusion-card></diversity-inclusion-card>
        </div>
        <div v-if="(baseRepo && (currentTab == 'risk'))">
          <risk-card></risk-card>
        </div>
        <div v-if="(baseRepo && (currentTab == 'value'))">
          <value-card></value-card>
        </div>
        <div v-if="(baseRepo && (currentTab == 'activity'))" id="activity">
          <base-repo-activity-card></base-repo-activity-card>
          <base-repo-ecosystem-card></base-repo-ecosystem-card>
          <div id="comparisonCards" v-bind:class="{ hidden: !comparedRepos.length }" v-for="repo in comparedRepos">
            <compared-repo-activity-card :comparedTo="repo"></compared-repo-activity-card>
          </div>
        </div>
        <div v-if="(baseRepo && (currentTab == 'experimental'))">
          <experimental-card></experimental-card>
          <div id="comparisonCards" v-bind:class="{ hidden: !comparedRepos.length }" v-for="repo in comparedRepos">
            <compared-repo-experimental-card :comparedTo="repo"></compared-repo-experimental-card>
          </div>
        </div>
        <div v-if="(gitRepo && (currentTab == 'git'))">
          <git-card></git-card>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import MainControls from './MainControls'
import AllMetricsStatusCard from './AllMetricsStatusCard'
import BaseRepoActivityCard from './BaseRepoActivityCard'
import BaseRepoEcosystemCard from './BaseRepoEcosystemCard'
import ComparedRepoActivityCard from './ComparedRepoActivityCard'
import GrowthMaturityDeclineCard from './GrowthMaturityDeclineCard'
import ComparedRepoGrowthMaturityDeclineCard from './ComparedRepoGrowthMaturityDeclineCard'
import RiskCard from './RiskCard'
import ValueCard from './ValueCard'
import DiversityInclusionCard from './DiversityInclusionCard'
import GitCard from './GitCard'
import ExperimentalCard from './ExperimentalCard'
import ComparedRepoExperimentalCard from './ComparedRepoExperimentalCard'
import DownloadedReposCard from './DownloadedReposCard'

module.exports = {
  components: {
    MainControls,
    AllMetricsStatusCard,
    BaseRepoActivityCard,
    BaseRepoEcosystemCard,
    ComparedRepoActivityCard,
    GrowthMaturityDeclineCard,
    ComparedRepoGrowthMaturityDeclineCard,
    RiskCard,
    ValueCard,
    DiversityInclusionCard,
    GitCard,
    ExperimentalCard,
    ComparedRepoExperimentalCard,
    DownloadedReposCard
  },
  data() {
    return {
      downloadedRepos: [],
      isCollapsed: false
    }
  },
  computed: {
    hasState() {
      return this.$store.state.hasState
    },
    baseRepo() {
      return this.$store.state.baseRepo
    },
    gitRepo() {
      return this.$store.state.gitRepo
    },
    comparedRepos() {
      return this.$store.state.comparedRepos
    },
    currentTab() {
      return this.$store.state.tab
    },
  },
  methods: {
    collapseText (){
      this.isCollapsed = !this.isCollapsed;
      if(!this.isCollapsed) {
        $(this.$el).find('.section').addClass('collapsed')
      }
      else $(this.$el).find('.section').removeClass('collapsed')
    },
    onRepo (e) {
      this.$store.commit('setRepo', {
        githubURL: e.target.value
      })
    },
    changeTab (e) {
      this.$store.commit('setTab', {
        tab: e.target.dataset['value']
      })
      e.preventDefault();
    },
    btoa(s) {
      return window.btoa(s)
    }
  }
}
</script>

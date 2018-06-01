<template>
  <div>

    <nav class="tabs">
      <ul>
        <li :class="{ active: (currentTab == 'gmd') }"><a href="#" @click="changeTab" data-value="gmd">Growth, Maturity, and Decline</a></li>
        <li :class="{ active: (currentTab == 'diversityInclusion') }"><a href="#" @click="changeTab" data-value="diversityInclusion">Diversity and Inclusion</a></li>
        <li :class="{ active: (currentTab == 'risk') }"><a href="#" @click="changeTab" data-value="risk">Risk</a></li>
        <li :class="{ active: (currentTab == 'value') }"><a href="#" @click="changeTab" data-value="value">Value</a></li>
        <li :class="{ active: (currentTab == 'activity') }"><a href="#" @click="changeTab" data-value="activity">Activity</a></li>
        <li :class="{ active: (currentTab == 'experimental') }"><a href="#" @click="changeTab" data-value="experimental">Experimental</a></li>
      </ul>
    </nav>

    <section :class="{ hidden: baseRepo, unmaterialized: true }">
      <h3>Enter a GitHub URL to get started</h3>
      <input type="text" class="search reposearch" placeholder="GitHub URL" @change="onRepo"/>
    </section>

    <div ref="cards">
      <div v-if="(baseRepo && (currentTab == 'gmd'))">
        <growth-maturity-decline-card></growth-maturity-decline-card>
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
      <div v-if="(baseRepo && (currentTab == 'experimental'))">
        <experimental-card></experimental-card>
      </div>
      <div v-if="(baseRepo && (currentTab == 'activity'))" id="activity">
        <base-repo-activity-card></base-repo-activity-card>
        <base-repo-ecosystem-card></base-repo-ecosystem-card>
        <div id="comparisonCards" v-bind:class="{ hidden: !comparedRepos.length }" v-for="repo in comparedRepos">
          <compared-repo-activity-card :comparedTo="repo"></compared-repo-activity-card>
        </div>
      </div>
      <section :class="{ hidden: !baseRepo, unmaterialized: true }">
        <h3>Compare repository</h3>
        <input type="text" class="search reposearch" placeholder="GitHub URL" @change="onCompare"/>
      </section>
    </div>
  </div>
</template>

<script>
import BaseRepoActivityCard from './BaseRepoActivityCard'
import BaseRepoEcosystemCard from './BaseRepoEcosystemCard'
import ComparedRepoActivityCard from './ComparedRepoActivityCard'
import GrowthMaturityDeclineCard from './GrowthMaturityDeclineCard'
import RiskCard from './RiskCard'
import ValueCard from './ValueCard'
import DiversityInclusionCard from './DiversityInclusionCard'
import ExperimentalCard from './ExperimentalCard'

module.exports = {
  components: {
    BaseRepoActivityCard,
    BaseRepoEcosystemCard,
    ComparedRepoActivityCard,
    GrowthMaturityDeclineCard,
    RiskCard,
    ValueCard,
    DiversityInclusionCard,
    ExperimentalCard
  },
  data() {
    return {
      currentTab: 'gmd'
    }
  },
  computed: {
    baseRepo() {
      return this.$store.state.baseRepo
    },
    comparedRepos() {
      return this.$store.state.comparedRepos
    }
  },
  methods: {
    onRepo (e) {
      this.$store.commit('setBaseRepo', {
        url: e.target.value
      })
    },
    onCompare (e) {
      this.$store.commit('addComparedRepo', {
        url: e.target.value
      })
    },
    changeTab (e) {
      this.currentTab = e.target.dataset['value']
      e.preventDefault();
    }
  }
}
</script>
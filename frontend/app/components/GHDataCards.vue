<template>
  <div ref="cards" class="content">
    <section :class="{ hidden: baseRepo, unmaterialized: true }">
      <h3>Enter a GitHub URL to get started</h3>
      <input type="text" class="search reposearch" placeholder="GitHub URL" @change="onRepo"/>
    </section>
    <div v-bind:class="{ hidden: !baseRepo }">
      <base-repo-activity-card></base-repo-activity-card>
      <base-repo-ecosystem-card></base-repo-ecosystem-card>
    </div>
    <div id="comparisonCards" v-bind:class="{ hidden: !comparedRepos.length }" v-for="repo in comparedRepos">
      <compared-repo-activity-card :comparedTo="repo"></compared-repo-activity-card>
    </div>
    <section :class="{ hidden: !baseRepo, unmaterialized: true }">
      <h3>Compare repository</h3>
      <input type="text" class="search reposearch" placeholder="GitHub URL" @change="onCompare"/>
    </section>
  </div>
</template>

<script>
import BaseRepoActivityCard from './BaseRepoActivityCard'
import BaseRepoEcosystemCard from './BaseRepoEcosystemCard'
import ComparedRepoActivityCard from './ComparedRepoActivityCard'

module.exports = {
  components: {
    BaseRepoActivityCard,
    BaseRepoEcosystemCard,
    ComparedRepoActivityCard
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
    }
  }
}
</script>
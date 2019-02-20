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
import AugurHeader from '../components/AugurHeader.vue'
import MetricsStatusCard from '../components/MetricsStatusCard.vue'
import BaseRepoActivityCard from '../components/BaseRepoActivityCard.vue'
import BaseRepoEcosystemCard from '../components/BaseRepoEcosystemCard.vue'
import GrowthMaturityDeclineCard from '../components/GrowthMaturityDeclineCard'
import RiskCard from '../components/RiskCard'
import ValueCard from '../components/ValueCard'
import DiversityInclusionCard from '../components/DiversityInclusionCard'
import GitCard from '../components/GitCard'
import OverviewCard from '../components/OverviewCard.vue'
import ExperimentalCard from '../components/ExperimentalCard'
import DownloadedReposCard from '../components/DownloadedReposCard.vue'
import MainControls from '../components/MainControls.vue'
import LoginForm from '../components/LoginForm'
import { mapState } from 'vuex'

module.exports = {
  props: ['owner', 'repo', 'domain', 'comparedowner', 'comparedrepo', 'groupid'],
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
  mounted() {
    console.log("MOUNTED")
  },
  created() {

    console.log("IT IS WORKING NOW")
    // if(this.repo || this.groupid){
    //   this.$store.commit("resetTab")
    //   // this.$store.commit('setTab', {
    //   //   tab: this.tab
    //   // })
    //   if (this.$router.history.current.name == "git"){
    //     this.$store.commit('setRepo', {
    //       gitURL: this.repo
    //     })
    //   } else if (!this.groupid){
    //     if (this.repo.includes('github')) {
    //       this.$store.commit('setRepo', {
    //         gitURL: this.repo
    //       })
    //     } else {
    //       this.$store.commit('setRepo', {
    //         githubURL: this.owner + '/' + this.repo
    //       })
    //     }
    //   }
    //   if(this.comparedrepo) { 
    //     this.$store.commit('addComparedRepo', {
    //       githubURL: this.comparedowner + '/' + this.comparedrepo
    //     })
    //   }
    //   if(this.groupid){
    //     let repos = this.groupid.split('+')
    //     if (repos[0].includes('github')) {
    //       this.$store.commit('setRepo', {
    //         gitURL: repos[0]
    //       })
    //     } else {
    //       this.$store.commit('setRepo', {
    //         githubURL: repos[0]
    //       })
    //     }
    //     repos.shift()
    //     // repos.pop()
    //     repos.forEach((cmprepo) => {
    //       this.$store.commit('addComparedRepo', {
    //         githubURL: cmprepo
    //       })
    //     })
    //   }
    // }
  },
  beforeRouteEnter (to, from, next) {
    // called before the route that renders this component is confirmed.
    // does NOT have access to `this` component instance,
    // because it has not been created yet when this guard is called!
    console.log("HIHKLJKLEJ")
  },
  watch: {
    '$route': function (to, from) {
      if (to.path != from.path)
        window.location.reload()
        // window.location.replace(to.path)
    }
  },
  methods: {
    onRepo (e) {
      let repo = window.AugurAPI.Repo({
          githubURL: e.target.value
        })
      if(!repo.batch(['codeCommits'], true)[0]){
        alert("The repo " + repo.githubURL + " could not be found. Please try again.")
      } else {
        this.$store.commit('resetBaseRepo')
        this.$store.commit('setRepo', {
          githubURL: e.target.value
        })
        this.$router.push({
          name: 'gmd',
          params: {owner: repo.owner, repo: repo.name}
        })

      }
      
    }
  }
}


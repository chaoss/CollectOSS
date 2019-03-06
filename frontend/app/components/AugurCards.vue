<template>
   
  <div>
    <div class="fullwidth">
        <augur-header></augur-header>
    </div>
   
    <!-- content to show if app has no state yet -->
    <div :class="{ hidden: hasState }">
       <!--  <user-dashboard></user-dashboard>
            <add-new-project></add-new-project>
           <login-form></login-form> 
        <forgot-password></forgot-password>
        <password-reset></password-reset>
        <new-user></new-user> --> 
      <section class="unmaterialized">
        <div id="collapse">
          <h3>Downloaded Git Repos by Project</h3>
          <!--<h3 v-if="isCollapsed" @click="collapseText">Downloaded Git Repos by Project,  <span style="font-size:16px">&#9660</span></h3>
          <h3 v-else @click="collapseText">Downloaded Git Repos by Project  <span style="font-size:16px">&#9654</span></h3>-->
        </div>
        <downloaded-repos-card></downloaded-repos-card>
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
          <li :class="{ active: (currentTab == 'overview'), hidden: comparedRepos.length < 2 }"><a href="#" @click="changeTab" data-value="overview">Group Overview</a></li>
          <li :class="{ active: (currentTab == 'openended'), hidden: comparedRepos.length > 0 }"><a href="#" @click="changeTab" data-value="openended">Open Ended Questions</a></li>
        </ul>
      </nav>

      <div ref="cards">
        <main-controls></main-controls>
        <div v-if="(baseRepo && (currentTab == 'gmd'))" :key="update">
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
        <div v-if="(baseRepo && (currentTab == 'activity'))" id="activity">
          <base-repo-activity-card></base-repo-activity-card>
          <base-repo-ecosystem-card></base-repo-ecosystem-card>
        </div>
        <div v-if="(baseRepo && (currentTab == 'experimental'))">
          <experimental-card></experimental-card>
        </div>
        <div v-if="(gitRepo && (currentTab == 'git'))">
          <git-card></git-card>
        </div>
        <div v-if="(comparedRepos.length >= 2 && (currentTab == 'overview'))">
          <overview-card></overview-card>
        </div>
        <div v-if="(comparedRepos.length == 0 && (currentTab == 'openended'))">
          <overview-card></overview-card>
        </div>
      </div>
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
  props: ['tab', 'owner', 'repo', 'domain', 'comparedowner', 'comparedrepo', 'groupid'],
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
    '$route': function (to, from) {
      if (to.path != from.path)
        // window.location.reload()
        window.location.replace(to.path)
    }
  },
  data() {
    return {
      downloadedRepos: [],
      isCollapsed: false,
      mapGroup: {1: this.$store.state.comparedRepos},
      extra: false,
      update: 0
    }
  },
  computed: {
    // ...mapState()
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
    goBack () {
      window.history.length > 1
        ? this.$router.go(-1)
        : this.$router.push('/')
    },
  },
  methods: {
    collapseText () {
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
      
      let repo = this.repo

      if(this.$store.state.comparedRepos.length == 1){
          this.$router.push({
          name: 'singlecompare',
          params: {tab: e.target.dataset['value'], owner: this.owner, repo: this.repo, comparedowner: this.comparedowner, comparedrepo: this.comparedrepo}
        })        
      } else if (this.$store.state.comparedRepos.length > 1) {
        this.$router.push({
          name: 'group',
          params: {tab: e.target.dataset['value'], groupid: this.groupid}
        })
      } else if (this.$router.history.current.name == "singlegit") {
        this.$router.push({
          name: 'singlegit',
          params: {tab: e.target.dataset['value'], repo: this.repo}
        })
      } else {
        this.$router.push({
          name: 'single',
          params: {tab: e.target.dataset['value'], owner: this.owner, repo: this.repo}
        })

      }
      
    },
    btoa(s) {
      return window.btoa(s)
    }
  }
}
</script>

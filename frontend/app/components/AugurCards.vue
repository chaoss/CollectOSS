<template>
   
  <div>
    <augur-header></augur-header>
    <!-- content to show if app has no state yet -->
    <div :class="{ hidden: hasState }">
      <!-- <login-form></login-form> -->
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
        </ul>
      </nav>

      <div ref="cards">
        <main-controls></main-controls>
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
      </div>
    </div>
  </div>
</template>

<script>
import MainControls from './MainControls'
import AugurHeader from './AugurHeader'
import MetricsStatusCard from './MetricsStatusCard'
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
import LoginForm from './LoginForm'
import { mapState } from 'vuex'

module.exports = {
  props: ['tab', 'owner', 'repo', 'domain', 'comparedowner', 'comparedrepo', 'groupid'],
  components: {
    MainControls,
    AugurHeader,
    MetricsStatusCard,
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
    DownloadedReposCard,
    LoginForm
  },
  created() {
    if(!this.groupid)
      this.mapGroup[1] = this.$store.state.comparedRepos
    if(this.repo){
      console.log("domain:", this.domain, this.owner)
      if (this.domain && this.owner){
        console.log("if", this.owner, this.repo)
        this.$store.commit('setGitRepo', {
          gitURL: this.owner + '/' + this.repo,
          domain: this.domain
        })
      }
      else{
        console.log("ELSE", this.owner, this.repo)
        let owner = this.owner ? this.owner : this.domain

        this.$store.commit('setRepo', {
          githubURL: owner + '/' + this.repo
        })

      }
      this.$store.commit('setTab', {
        tab: this.tab
      })
      if(this.comparedrepo) { 
        this.$store.commit('addComparedRepo', {
          githubURL: this.comparedowner + '/' + this.comparedrepo
        })
      }
      if (localStorage.getItem('groupid')) {
        if (localStorage.getItem('domain'))
          this.$store.commit('setGitRepo', {
            gitURL: localStorage.getItem('owner') + '/' + localStorage.getItem('repo'),
            domain: localStorage.getItem('domain')
          })
        else{
          this.$store.commit('setRepo', {
            githubURL: localStorage.getItem('owner') + '/' + localStorage.getItem('repo'),
          })
        }
        JSON.parse(localStorage.getItem('group')).forEach((repo) => {
          this.$store.commit('addComparedRepo', {
            githubURL: repo
          })
        })
      } 
      localStorage.clear()
    }
  },
  watch: {
    comparedRepos: function(){
      console.log(this.$store.state.comparedRepos.length, "second")
      console.log(this.groupid)
      localStorage.setItem('group', JSON.stringify(this.$store.state.comparedRepos));  
      if (this.gitRepo)
        localStorage.setItem('domain', this.domain)
      
      if(this.$store.state.comparedRepos.length > 1){
        localStorage.setItem("groupid", this.groupid)
        localStorage.setItem('repo', this.repo)
        localStorage.setItem('owner', this.owner)
      }
      console.log("GROUP HERE", localStorage.getItem('owner'))
    }
  },
  data() {
    return {
      downloadedRepos: [],
      isCollapsed: false,
      mapGroup: {1: this.$store.state.comparedRepos},
      extra: false
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
      
      let link = null
      let repo = this.$store.state.gitRepo ? 'github/' + this.$store.state.baseRepo : this.$store.state.baseRepo
      if (this.$store.state.comparedRepos.length == 1)
        link = '/' + e.target.dataset['value'] + '/' + repo + '/comparedto/' + this.$store.state.comparedRepos[0]
      else if (this.$store.state.comparedRepos.length > 1)
        link = '/' + e.target.dataset['value'] + '/groupid/1'
      else
        link = '/' + e.target.dataset['value'] + '/' + this.$store.state.baseRepo
      if(this.$store.state.comparedRepos.length == 1){
          this.$router.push({
          name: 'singlecompare',
          params: {tab: e.target.dataset['value'], domain: this.domain, owner: this.owner, repo: this.repo, comparedowner: this.comparedowner, comparedrepo: this.comparedrepo}
        })        
      } else if (this.$store.state.comparedRepos.length > 1) {
        this.$router.push({
          name: 'group',
          params: {tab: e.target.dataset['value'], groupid: 1}
        })
      } else {
        this.$router.push({
          name: 'single',
          params: {tab: e.target.dataset['value'], domain: this.domain, owner: this.owner, repo: this.repo, comparedowner: this.comparedowner, comparedrepo: this.comparedrepo}
        })
      }
      
    },
    btoa(s) {
      return window.btoa(s)
    }
  }
}
</script>

<template>
   
  <div>
    <div class="fullwidth">
        <augur-header></augur-header>
    </div>
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
import GrowthMaturityDeclineCard from './GrowthMaturityDeclineCard'
import RiskCard from './RiskCard'
import ValueCard from './ValueCard'
import DiversityInclusionCard from './DiversityInclusionCard'
import GitCard from './GitCard'
import ExperimentalCard from './ExperimentalCard'
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
    GrowthMaturityDeclineCard,
    RiskCard,
    ValueCard,
    DiversityInclusionCard,
    GitCard,
    ExperimentalCard,
    DownloadedReposCard,
    LoginForm
  },
  created(to, from, next) {
    if(this.repo || this.groupid){
      this.$store.commit("resetTab")
      this.$store.commit('setTab', {
        tab: this.tab
      })
      if (this.$router.history.current.name == "singlegit"){
        this.$store.commit('setRepo', {
          gitURL: this.repo
        })
      } else if (!this.groupid){
        if (this.repo.includes('github')) {
          this.$store.commit('setRepo', {
            gitURL: this.repo
          })
        } else {
          this.$store.commit('setRepo', {
            githubURL: this.owner + '/' + this.repo
          })
        }
      }
      if(this.comparedrepo) { 
        this.$store.commit('addComparedRepo', {
          githubURL: this.comparedowner + '/' + this.comparedrepo
        })
      }
      if(this.groupid){
        let repos = this.groupid.split('+')
        if (repos[0].includes('github')) {
          this.$store.commit('setRepo', {
            gitURL: repos[0]
          })
        } else {
          this.$store.commit('setRepo', {
            githubURL: repos[0]
          })
        }
        repos.shift()
        // repos.pop()
        repos.forEach((cmprepo) => {
          this.$store.commit('addComparedRepo', {
            githubURL: cmprepo
          })
        })
      }
    }
  },
  watch: {
    // comparedRepos: function(){
    //   localStorage.setItem('group', JSON.stringify(this.$store.state.comparedRepos));
       
    //   if (this.gitRepo != null){
    //     localStorage.setItem('domain', this.domain)
    //     localStorage.setItem('git', this.$store.state.gitRepo)
    //   }
    //   console.log(localStorage.getItem('git'), "this is it") 
    //   localStorage.setItem('base', this.$store.state.baseRepo)
      
    //   if(this.$store.state.comparedRepos.length > 1){
    //     localStorage.setItem("groupid", this.groupid)
    //     localStorage.setItem('repo', this.repo)
    //     localStorage.setItem('owner', this.owner)
    //   }
    // },
    '$route': function (to, from) {
      if (to.name != from.name)
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

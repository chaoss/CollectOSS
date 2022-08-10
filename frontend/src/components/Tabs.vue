<!-- #SPDX-License-Identifier: MIT -->
<template>
  <nav class="tabs">
        <ul>
          <li :class="{ active: (currentTab == 'git'), hidden: !gitRepo }"><a href="#" @click="changeTab" data-value="git">Git</a></li>
          <li :class="{ active: (currentTab == 'overview'), hidden: !gitRepo }"><a href="#" @click="changeTab" data-value="overview">Overview</a></li>
          <li :class="{ active: (currentTab == 'gmd') }"><a href="#" @click="changeTab" data-value="gmd">Evolution</a></li>
          <li :class="{ active: (currentTab == 'activity') }"><a href="#" @click="changeTab" data-value="activity">Activity</a></li>
          <li :class="{ active: (currentTab == 'experimental') }"><a href="#" @click="changeTab" data-value="experimental">Experimental</a></li>
          <li :class="{ active: (currentTab == 'issues') }"><a href="#" @click="changeTab" data-value="issues">Issues</a></li>
        </ul>
      </nav>
</template>

<script>
export default {
  props: ['owner', 'repo', 'comparedowner', 'comparedrepo', 'groupid'],
  computed: {
    gitRepo () {
      return this.$store.state.gitRepo
    },
    currentTab () {
      return this.$store.state.tab
    },
    baseRepo () {
      return this.$store.state.baseRepo
    },
    comparedRepos () {
      return this.$store.state.comparedRepos
    }
  },
  methods: {
    changeTab (e) {
      console.log("changing tab to: ", e.target.dataset.value)
      this.$store.commit('setTab', {
        tab: e.target.dataset.value
      })
      if(this.$store.state.comparedRepos.length == 1) {
        let owner = this.gitRepo ? null : this.baseRepo.split('/')[0]
        let repo = this.gitRepo ? this.gitRepo : this.baseRepo.split('/')[1]
        let comparedowner = this.comparedRepos[0].split('/').length > 2 ? null : this.comparedRepos[0].split('/')[0]
        let comparedrepo = this.comparedRepos[0].split('/').length > 2 ? this.comparedRepos[0] : this.comparedRepos[0].split('/')[1]
        let name = e.target.dataset['value'] + "compare"
        this.$router.push({
          name,
          params: {owner, repo, comparedowner, comparedrepo}
        })
      } else if (this.$store.state.comparedRepos.length > 1) {
        let groupid = (this.gitRepo ? String(this.gitRepo) + '+' : String(state.baseRepo) + "+")
            this.comparedRepos.forEach((repo) => {
              groupid += (String(repo) + '+')
            })
        let name = e.target.dataset['value'] + "group"
        this.$router.push({
          name,
          params: {groupid}
        })
      } else {
        let owner = this.gitRepo ? null : this.baseRepo.split('/')[0]
        let repo = this.gitRepo ? this.gitRepo : this.baseRepo.split('/')[1]
        this.$router.push({
          name: e.target.dataset['value'],
          params: {owner, repo}
        })
      }

    },
  }
};
</script>

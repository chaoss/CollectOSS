<template>
  <d-container fluid class="main-content-container px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <!-- <span class="text-uppercase page-subtitle">Components</span> -->
        <h3 class="page-title" style="font-size: 1rem">Insights</h3>
      </div>
    </div>

    <!-- First Row of Posts -->

        <d-row>
          <div v-if="!loadedGroups" class="col-md-8 col-lg-9">
            <spinner style="top: 30%; position: relative; transform: translateY(-50%);"></spinner>
          </div>
          <d-col v-if="loadedGroups" v-for="(group, idx) in repo_groups.slice(0,3)" :key="idx" lg="3" md="4" sm="8" class="mb-4">
            <spinner v-if="!values[testEndpoints[idx]]['loaded']"style="top: 30%; position: relative; transform: translateY(-50%);"></spinner>
            <d-card v-if="values[testEndpoints[idx]]['loaded']" class="card-small card-post card-post--1">
              <div class="card-post__image">
                <d-badge pill :class="['card-post__category', 'bg-' + themes[idx] ]">{{ group.rg_name }}</d-badge>
                <insight-chart style="transform: translateX(-30px)" :color="colors[idx]" v-if="loaded" :data="values[testEndpoints[idx]]"></insight-chart>

                <div class="card-post__author d-flex">
                  <a href="#" :style="getColor(idx)" class="card-post__author-avatar card-post__author-avatar--small" style="text-indent: 0; text-align: center; font-size: 1rem">
                    <i class="material-icons" style="position: relative; top: 50%; transform: translateY(-60%)">{{ getDirection(idx) }}</i>
                  </a>
                </div>
              </div>
              <d-card-body>
                <h5 class="card-title">
                  <a href="#" class="text-fiord-blue">{{ getOwner(repo_relations[group.rg_name][0].url) }}/{{ getRepo(repo_relations[group.rg_name][0].url) }}</a>
                </h5>
                <p class="card-text d-inline-block mb-1" style="font-size: .75rem">This repository {{ getPhrase(idx) }} in {{ testEndpoints[idx] }} in the past {{ testTimeframes[idx] }}</p>
                <span class="text-muted" style="font-size: .75rem">{{ testTimeframes[idx] }}</span>
              </d-card-body>
            </d-card>
          </d-col>
          <d-col lg="3" md="4" sm="8" class="mb-4" style="font-size: .7rem">
            <d-card class="card-small card">
              <div class="border-bottom card-header">
                <h6 class="m-0" style="font-size: .7rem">Worker Status</h6>
                <span class="ml-auto text-right text-semibold text-reagent-gray">Tasks Completed</span>
                <div class="block-handle"></div>
              </div>
              <div class="p-0 card-body">
                <div class="list-group-small list-group list-group-flush">
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue" style="font-size: .85rem">GitHub Shallow</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray" style="font-size: .85rem">19,291 / 21,512</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue" style="font-size: .85rem">BugZilla</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray" style="font-size: .85rem">11,201 / 14,213</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue" style="font-size: .85rem">Facade</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray" style="font-size: .85rem">9,291 / 10,634</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue" style="font-size: .85rem">Github API</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray" style="font-size: .85rem">8,281 / 15,351</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue" style="font-size: .85rem">GitHub Deep</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray" style="font-size: .85rem">7,128 / 18,432</span>
                  </div>
                </div>
              </div>
              <d-card-footer class="border-top">
                <d-row>

                  <!-- Time Frame -->
                  <d-col class="col-5">
                    <d-select size="sm" value="last-week" style="max-width: 130px;">
                      <option value="last-week">Sort</option>
                      <option value="today">?</option>
                      <option value="last-month">?</option>
                      <option value="last-year">?</option>
                    </d-select>
                  </d-col>

                  <!-- View Full Report -->
                  <d-col class="text-right view-report col-7" style="font-size: .6rem">
                    <a href="#">Overview of all workers &rarr;</a>
                  </d-col>

                </d-row>
              </d-card-footer>
            </d-card>
          </d-col>
        </d-row>

        <div style="transform: translateY(-20px)">
          <div class="page-header row no-gutters py-4" style="padding-top: 5 !important;">
            <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
              <!-- <span class="text-uppercase page-subtitle">Components</span> -->
              <h3 class="page-title" style="font-size: 1rem">Most Frequent Repo Groups</h3>
            </div>
          </div>
          <!-- Second Row of Posts -->
          <d-row>
            <div style="padding-top: 3rem" v-if="!loadedGroups" class="col-md-8 col-lg-9">
              <spinner></spinner>
            </div>

            <d-col v-if="loadedGroups" v-for="(group, idx) in repo_groups.slice(0,6)" :key="idx" lg="4" sm="12" class="mb-4">
              
              <d-card class="card-small card">
                <div class="border-bottom card-header">
                  <h6 class="m-0">{{ group.rg_name }}</h6>
                  <div class="block-handle"></div>
                </div>
                <div class="p-0 card-body">
                  <div class="list-group-small list-group list-group-flush">
                    <div v-for="(repo, i) in repo_relations[group.rg_name].slice(0,5)" class="d-flex px-3 list-group-item" style="text-align: left">
                      <d-link :to="{name: 'repo_overview', params: {repo: repo.url}}" @click="onGitRepo(repo)">
                        <span class="text-semibold text-fiord-blue" style="font-size: .65rem; padding: 0">{{ repo.url }}</span>
                      </d-link>

                      <div v-if="!values[repo.url]['loaded']" class="col-12">
                        <spinner style="top: 80%; position: relative; transform: translateY(-50%);"></spinner>
                      </div>
                      <spark-chart v-if="values[repo.url]['values'] != null" :color="colors[idx]" :owner="repo.url" style="max-height: 50px; padding-bottom: 0px; margin-left:auto; margin-right:0;" :data="values[repo.url]['values']"/>
                    </div>
                  </div>
                </div>
              </d-card>
            </d-col>
          </d-row>
        </div>
  </d-container>
</template>

<script>
import SparkChart from '../components/charts/SparkChart.vue';
import InsightChart from '../components/charts/InsightChart.vue';
import Spinner from '../components/Spinner.vue';

export default {
  components: {
    SparkChart,
    InsightChart,
    Spinner
  },
  computed: {
  },
  data() {
    return {
      colors: ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      testEndpoints: ['codeCommits', 'closedIssues', 'openIssues'],
      testTimeframes: ['past 1 month', 'past 3 months', 'past 2 weeks'],
      repos: [],
      repo_groups: [],
      repo_relations: {},
      themes: ['dark', 'info', 'royal-blue', 'warning'],
      values: {},
      loadedGroups: false
    }
  },
  methods: {
    getOwner(url) {
      console.log(url)
      let first = url.indexOf(".")
      let last = url.lastIndexOf(".")
      let domain = null
      let owner = null
      let repo = null
      let extension = false

      if (first == last){ //normal github
        domain = url.substring(0, first)
        owner = url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.slice(url.lastIndexOf('/') + 1)
        console.log(owner+ "/" + repo)
        return owner
      } else if (url.slice(last) == '.git'){ //github with extension
        domain = url.substring(0, first)
        extension = true
        owner = url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.substring(url.lastIndexOf('/') + 1, url.length - 4)
        return owner
      } else { //gluster
        domain = url.substring(first + 1, last)
        owner = null //url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.slice(url.lastIndexOf('/') + 1)
        return domain
      }
    },
    getRepo(url){
      let first = url.indexOf(".")
      let last = url.lastIndexOf(".")
      let domain = null
      let owner = null
      let repo = null
      let extension = false

      if (first == last){ //normal github
        domain = url.substring(0, first)
        owner = url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.slice(url.lastIndexOf('/') + 1)
        return repo
      } else if (url.slice(last) == '.git'){ //github with extension
        domain = url.substring(0, first)
        extension = true
        owner = url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.substring(url.lastIndexOf('/') + 1, url.length - 4)
        return repo
      } else { //gluster
        domain = url.substring(first + 1, last)
        owner = null //url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.slice(url.lastIndexOf('/') + 1)
        return repo
      }
    },
    getColor (idx) {
      if (idx % 2 == 0)
        return 'color: green'
      else
        return 'color: red'
    },
    getDirection (idx) {
      if (idx % 2 == 0)
        return 'arrow_upward'
      else
        return 'arrow_downward'
    },
    getPhrase (idx) {
      if (idx % 2 == 0)
        return 'increased'
      else
        return 'declined'
    },
    onRepo (e) {
      this.$store.commit('setRepo', {
        githubURL: e.target.value
      })
    },
    onGitRepo (e) {
      this.$store.commit('setRepo', {
        gitURL: e.url
      })
    },
    getDownloadedRepos () {
      console.log("START")
      window.AugurAPI.getRepos().then((data) => {
        this.repos = data
        data.forEach((repo) => {
          // set loaded's to false
          this.values[repo.url] = {}
          this.values[repo.url].loaded = true
        })
        
        console.log("LOADED repos", this.repos)
        window.AugurAPI.getRepoGroups().then((data) => {
          $(this.$el).find('.spinner').removeClass('loader')
          $(this.$el).find('.spinner').removeClass('relative')
          this.repo_groups = data
          //move down between future relation endpoint
          this.repo_groups.forEach((group) => {
            this.repo_relations[group.rg_name] = this.repos.filter(function(repo){
              return repo.rg_name == group.rg_name
            })
          })
          this.loadedGroups = true
          this.loadMetrics()
          console.log("LOADED repo groups", this.repo_relations)
        })
      })
    },
    loadMetrics () {
      // Load data for insights
      let count = 0
      this.repo_groups.slice(0,3).forEach((group) => {
        
        let repo = window.AugurAPI.Repo({ gitURL: this.repo_relations[group.rg_name][0]['url'] })
        repo[this.testEndpoints[count]]().then((data) => {
          this.values[this.testEndpoints[count]]["values"] = data
          this.values[this.testEndpoints[count]]["loaded"] = true
          console.log("loaded insights for: ", this.testEndpoints[count], this.values[this.testEndpoints[count]])
        })
        count++
      })
      // Load data for spark charts
      this.repo_groups.forEach((group) => {
        this.repo_relations[group.rg_name].slice(0,6).forEach((repo) => {
          let api_repo = window.AugurAPI.Repo({ gitURL: repo['url'] })
          api_repo.codeCommits().then((data) => {
            console.log("about to load sparks")
            console.log(this.values[repo.url]['values'] != null)//values[repo.url]['values']

            this.values[repo.url]['values'] = data
            console.log("loaded sparks for: ", this.values[repo['url']])
            this.values[repo.url]['loaded'] = true
          })
        })
        
      })
    },
    btoa(s) {
      return window.btoa(s)
    }
  },
  created() {
    // Set all loaded's to false
    this.testEndpoints.forEach((endpoint) => {
      this.values[endpoint] = {}
      this.values[endpoint]['loaded'] = false
    })

    // Call our data collection methods
    this.getDownloadedRepos()
    
  },
}
</script>


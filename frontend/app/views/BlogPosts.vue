<template>
  <d-container fluid class="main-content-container px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <!-- <span class="text-uppercase page-subtitle">Components</span> -->
        <h3 class="page-title" style="font-size: 2rem">Insights</h3>
      </div>
    </div>

    <!-- First Row of Posts -->

        <d-row>
          <d-col v-for="(project, idx) in projects.slice(0,3)" :key="idx" lg="3" md="6" sm="12" class="mb-4">
            <d-card class="card-small card-post card-post--1">
              <div class="card-post__image">
                <d-badge pill :class="['card-post__category', 'bg-' + themes[idx] ]">{{ project }}</d-badge>
                <insight-chart style="transform: translateX(-30px)" :color="colors[idx]" v-if="loaded" :source="testEndpoints[idx]" owner="twitter" repo="twemoji"></insight-chart>

                <div class="card-post__author d-flex">
                  <a href="#" :style="getColor(idx)" class="card-post__author-avatar card-post__author-avatar--small" style="text-indent: 0; text-align: center; font-size: 2rem">
                    <i class="material-icons" style="position: relative; top: 50%; transform: translateY(-60%); ">{{ getDirection(idx) }}</i>
                  </a>
                </div>
              </div>
              <d-card-body>
                <h5 class="card-title">
                  <a href="#" class="text-fiord-blue">{{ getOwner(repos[project][0].url) }}/{{ getRepo(repos[project][0].url) }}</a>
                </h5>
                <p class="card-text d-inline-block mb-3">This repository {{ getPhrase(idx) }} in {{ testEndpoints[idx] }} in the past {{ testTimeframes[idx] }}</p>
                <span class="text-muted">{{ testTimeframes[idx] }}</span>
              </d-card-body>
            </d-card>
          </d-col>
          <d-col class="col-3">
            <d-card class="card-small card">
              <div class="border-bottom card-header">
                <h6 class="m-0">Worker Status</h6>
                <span class="ml-auto text-right text-semibold text-reagent-gray">Tasks Completed</span>
                <div class="block-handle"></div>
              </div>
              <div class="p-0 card-body">
                <div class="list-group-small list-group list-group-flush">
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">GitHub Shallow</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">19,291 / 21,512</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">BugZilla</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">11,201 / 14,213</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">Facade</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">9,291 / 10,634</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">Github API</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">8,281 / 15,351</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">GitHub Deep</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">7,128 / 18,432</span>
                  </div>
                </div>
              </div>
              <d-card-footer class="border-top">
                <d-row>

                  <!-- Time Frame -->
                  <d-col>
                    <d-select size="sm" value="last-week" style="max-width: 130px;">
                      <option value="last-week">Sort</option>
                      <option value="today">?</option>
                      <option value="last-month">?</option>
                      <option value="last-year">?</option>
                    </d-select>
                  </d-col>

                  <!-- View Full Report -->
                  <d-col class="text-right view-report col-8">
                    <a href="#">All workers and priority options &rarr;</a>
                  </d-col>

                </d-row>
              </d-card-footer>
            </d-card>
          </d-col>
        </d-row>

        <div style="transform: translateY(-20px)">
          <div class="page-header row no-gutters py-4" style="padding-top: 0 !important;">
            <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
              <!-- <span class="text-uppercase page-subtitle">Components</span> -->
              <h3 class="page-title" style="font-size: 2rem">Most Frequent Projects</h3>
            </div>
          </div>
          <!-- Second Row of Posts -->
          <d-row>
            <d-col v-for="(project, idx) in projects.slice(0,3)" :key="idx" lg="4" sm="12" class="mb-4">
              <d-card class="card-small card">
                <div class="border-bottom card-header">
                  <h6 class="m-0">{{ project }}</h6>
                  <div class="block-handle"></div>
                </div>
                <div class="p-0 card-body">
                  <div class="list-group-small list-group list-group-flush">
                    <div v-for="(repo, i) in repos[project].slice(0,5)" class="d-flex px-3 list-group-item" style="text-align: left">
                      <d-link :to="{name: 'repo_overview', params: {repo: repo.url}}" @click="onGitRepo(repo)">
                        <span class="text-semibold text-fiord-blue" style="font-size: .65rem">{{ repo.url }}</span>
                      </d-link> 
                      <spark-chart v-if="loaded" :color="colors[idx]" style="max-height: 50px; padding-bottom: 10px; margin-left:auto; margin-right:0;" :owner="getOwner(repo.url)" :repo="getRepo(repo.url)" source="codeCommits"/>
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

export default {
  components: {
    SparkChart,
    InsightChart,
  },
  computed: {
  },
  data() {
    return {
      colors: ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      testEndpoints: ['codeCommits', 'closedIssues', 'openIssues'],
      testTimeframes: ['past 1 month', 'past 3 months', 'past 2 weeks'],
      repos: {},
      projects: [],
      themes: ['dark', 'info', 'royal-blue', 'warning'],
    }
  },
  methods: {
    getOwner(url) {
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
    getDownloadedRepos() {
      this.downloadedRepos = []
      window.AugurAPI.getDownloadedGitRepos().then((data) => {
        $(this.$el).find('.spinner').removeClass('loader')
        $(this.$el).find('.spinner').removeClass('relative')
        this.repos = window._.groupBy(data, 'project_name')
        this.projects = Object.keys(this.repos)
        let impRepos = []
        for (let i = 0; i < this.projects.length; i++) {
          impRepos.push(this.repos[this.projects[i]][0])
        }
        console.log("LOADED")
        this.loaded = true
        // window.AugurAPI.batchMapped(impRepos, ['codeCommits']).then((data) => {
        //   console.log("DATA", data)
        // }, () => {
        //   //this.renderError()
        // }) // end batch request
      })
    },
    btoa(s) {
      return window.btoa(s)
    }
  },
  created() {
    this.getDownloadedRepos()
  },
}
</script>


<template>
  <d-container fluid class="main-content-container px-4">
    <!--           <d-col lg="3" md="4" sm="8" class="mb-4" style="font-size: .7rem">
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

                  <d-col class="col-5">
                    <d-select size="sm" value="last-week" style="max-width: 130px;">
                      <option value="last-week">Sort</option>
                      <option value="today">?</option>
                      <option value="last-month">?</option>
                      <option value="last-year">?</option>
                    </d-select>
                  </d-col>

                  <d-col class="text-right view-report col-7" style="font-size: .6rem">
                    <a href="#">Overview of all workers &rarr;</a>
                  </d-col>

                </d-row>
              </d-card-footer>
            </d-card>
          </d-col> -->
  </d-container>
</template>

<script>
import SparkChart from '../components/charts/SparkChart.vue';
import InsightChart from '../components/charts/InsightChart.vue';
import TickChart from '../components/charts/TickChart'
import LinesOfCodeChart from '../components/charts/LinesOfCodeChart'
import NormalizedStackedBarChart from '../components/charts/NormalizedStackedBarChart'
import OneDimensionalStackedBarChart from '../components/charts/OneDimensionalStackedBarChart'
import HorizontalBarChart from '../components/charts/HorizontalBarChart'
import GroupedBarChart from '../components/charts/GroupedBarChart'
import StackedBarChart from '../components/charts/StackedBarChart'
import DynamicLineChart from '../components/charts/DynamicLineChart'
import DualLineChart from '../components/charts/DualLineChart'
import Spinner from '../components/Spinner'

export default {
  components: {
    SparkChart,
    InsightChart,
    TickChart,
    LinesOfCodeChart,
    NormalizedStackedBarChart,
    OneDimensionalStackedBarChart,
    HorizontalBarChart,
    GroupedBarChart,
    DynamicLineChart,
    StackedBarChart,
    DualLineChart,
    Spinner
  },
  computed: {
    repo () {
      return this.$store.state.baseRepo
    },
    gitRepo () {
      return this.$store.state.gitRepo
    },
    values () {
      console.log("getting values")
      let values = {}
      let repo = window.AugurAPI.Repo({ gitURL: this.gitRepo })
      repo.issuesClosed().then((data) => {
        values['issuesClosed'] = data
        this.loaded_overview = true
      })
      return values
    }
  },
  data() {
    return {
      colors: ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      testEndpoints: ['closedIssues', 'openIssues', 'codeCommits'],
      testTimeframes: ['past 1 month', 'past 3 months', 'past 2 weeks'],
      repos: {},
      projects: [],
      themes: ['dark', 'info', 'royal-blue', 'warning'],
      project: null,
      loaded_overview: false,
      loaded_evolution: false,
      loaded_issues: false,
      loaded_experimental: false,
      loaded_activity: false
    };
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
      let first = e.url.indexOf(".")
      let last = e.url.lastIndexOf(".")
      let domain = null
      let owner = null
      let repo = null
      let extension = false

      if (first == last){ //normal github
        domain = e.url.substring(0, first)
        owner = e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'))
        repo = e.url.slice(e.url.lastIndexOf('/') + 1)
      } else if (e.url.slice(last) == '.git'){ //github with extension
        domain = e.url.substring(0, first)
        extension = true
        owner = e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'))
        repo = e.url.substring(e.url.lastIndexOf('/') + 1, e.url.length - 4)
      } else { //gluster
        domain = e.url.substring(first + 1, last)
        owner = null //e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'))
        repo = e.url.slice(e.url.lastIndexOf('/') + 1)
      }
      this.$store.commit('setRepo', {
        gitURL: e.url
      })

      this.$store.commit('setTab', {
        tab: 'git'
      })

      this.$router.push({
        name: 'git',
        params: {repo: e.url}
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
    // this.getDownloadedRepos()
    let repo = window.AugurAPI.Repo({ gitURL: this.gitRepo })
    this.project = repo.rg_name
    // repo.facadeProject().then((data) => {
      // this.loaded=true
    // })
  },
}
</script>


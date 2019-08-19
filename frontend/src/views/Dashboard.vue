<template>
  <d-container fluid class="main-content-container px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="page-title" style="font-size: 1rem">Insights</h3>
      </div>
    </div>

    <!-- First Row of Posts -->

        <d-row>
          <div v-if="!loadedInsights" class="col-md-8 col-lg-9">
            <spinner style="padding: 1rem 0 1rem 0; position: relative; transform: translateY(-50%);"></spinner>
          </div>
          <d-col v-else v-for="(record, idx) in highest" :key="idx" lg="3" md="4" sm="8" class="mb-4">
            
            <d-card v-if="idx < 4" class="card-small card-post card-post--1">
              <div class="card-post__image">
                <d-badge pill :class="['card-post__category', 'bg-' + themes[idx] ]">{{ record.rg_name }}</d-badge>
                <insight-chart style="transform: translateX(-3.35rem)" :data="insights[record.rg_name][record.repo_git][record.ri_metric]" :url="record.repo_git" :color="colors[idx]"></insight-chart>

                <div class="card-post__author d-flex">
                  <a href="#" :style="colors[idx]" class="card-post__author-avatar card-post__author-avatar--small" style="text-indent: 0; text-align: center; font-size: 1rem">
                    <i class="material-icons" style="position: relative; top: 50%; transform: translateY(-60%)">{{ getDirection(insights[record.rg_name][record.repo_git][record.ri_metric]) }}</i>
                  </a>
                </div>
              </div>
              <d-card-body>
                <h5 class="card-title">
                  <a href="#" @click="onGitRepo(record)" class="text-fiord-blue">{{ record.repo_git.substr(19) }}</a>
                </h5>
                <p class="card-text d-inline-block mb-1" style="font-size: .75rem">This repository had a sharp {{ getPhrase(insights[record.rg_name][record.repo_git][record.ri_metric]) }}</p>
                <div class="row">
                  <div class="col col-5"><span class="text-muted" style="font-size: .75rem">{{ timeframes[record.repo_git] }}</span></div>
                  <!-- View Full Report -->
                  <d-col col sm="7" style="transform: translateX(-1rem) !important;">
                    <d-button size="sm" @click="onInspectInsight(insights[record.rg_name][record.repo_git][record.ri_metric])" style="color: white !important" class="d-flex btn-white ml-auto mr-auto ml-sm-auto mr-sm-0 mt-3 mt-sm-0">View Full Report &rarr;</d-button>
                  </d-col>
<!--                   <div class="col col-7"><span class="text-muted" style="font-size: .75rem"><a href="#" class="text-fiord-blue" @click="onInspectInsight(insights[record.rg_name][record.repo_git][record.ri_metric])">See more here...</a></span></div>
 -->                </div>
              </d-card-body>
            </d-card>
          </d-col>
        </d-row>

        <div style="transform: translateY(-0px)">
          <div class="page-header row no-gutters py-4" style="padding-top: 5 !important;">
            <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
              <!-- <span class="text-uppercase page-subtitle">Components</span> -->
              <h3 class="page-title" style="font-size: 1rem">Most Frequent Repo Groups</h3>
            </div>
          </div>
          <!-- Second Row of Posts -->
          <d-row>
            <div style="padding-top: 3rem" v-if="apiGroups == {}" class="col-md-8 col-lg-9">
              <spinner></spinner>
            </div>

            <d-col v-else v-for="(group, idx) in Object.keys(insights).slice(0,6)" :key="idx" lg="4" sm="12" class="mb-4">
              <d-card class="card-small card">
                <div class="border-bottom card-header">
                  <h6 class="m-0">{{ group }}</h6>
                  <div class="block-handle"></div>
                </div>
                <div class="p-0 card-body">
                  <div class="list-group-small list-group list-group-flush">
                    <div v-for="(repo, i) in Object.keys(insights[group]).slice(0,5)" class="d-flex px-3 list-group-item" style="text-align: left">
                      <a href="#" @click="onGitRepo(repo)">
                        <span class="text-semibold text-fiord-blue" style="font-size: .65rem; padding: 0">{{ repo }}</span>
                      </a>
                      <div v-if="loadedInsights" v-for="metric in Object.keys(insights[group][repo]).slice(0,1)" style="margin: 0 0 0 auto; float:right">
                        <spark-chart :color="colors[idx]" :url="repo" :data="insights[group][repo][metric]" style="max-height: 50px; padding-bottom: 0px; "/>
                      </div>
                      
                    </div>
                  </div>
                </div>
              </d-card>
            </d-col>
          </d-row>
        </div>
  </d-container>
</template>

<script lang="ts">
import {mapActions, mapGetters, mapMutations} from "vuex";
import Component from 'vue-class-component';
import Vue from 'vue';
import SparkChart from '../components/charts/SparkChart.vue';
import InsightChart from '../components/charts/InsightChart.vue';
import Spinner from '../components/Spinner.vue';

interface FlexObject<TValue> {
  [id: string]: TValue;
}

@Component({
  methods: {
    ...mapActions('common',[
      'loadRepos',
      'loadRepoGroups',
      'createAPIObjects',
      'endpoint',
      'addRepoGroup'
    ])
  },
  computed: {
    ...mapGetters('common', [
      'repoRelations',
      'repoGroups',
      'repos',
      'apiRepos',
      'apiGroups',
      'cache'
      // 'repoRelations'
    ]),
    // repoRelations() {
    //   return this.$store.getters['common/repoRelations']
    // },
    // repoGroups() {
    //   return this.$store.getters['common/repoGroups']
    // },
    // repos() {
    //   return this.$store.getters['common/repos']
    // },
    // apiRepos() {
    //   return this.$store.getters['common/apiRepos']
    // }
  },
  components: {
    SparkChart,
    InsightChart,
    Spinner
  }
})
export default class Dashboard extends Vue {
  
  // Data properties
  chart: any = null //"#343A40", 
  colors: string[] = ["#24a2b7", "#FF3647","#159dfb", "#FFC107","#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"];
  tempInsightEndpoints: string[] = ['issuesClosed', 'codeChangesLines', 'issueNew'];
  tempInsightRepos: any[] = [];
  tempInsightTimeframes: string[] = ['past 1 month', 'past 3 months', 'past 2 weeks'];
  themes: string[] = ['info', 'danger','royal-blue', 'warning', 'dark'];
  loadedRelations: boolean = false
  loadedInsights: boolean = false
  desiredReposPerGroup: number = 5
  insights: any = {}
  timeframes: any = {}
  test: any[] = ['https://github.com/rails/ruby-coffee-script.git', 'https://github.com/Comcast/Hygieia.git','https://github.com/apache/jclouds-site.git',
    'https://github.com/apache/karaf-jclouds.git', 'https://github.com/openssl/openssl', 'https://github.com/rails/ruby-coffee-script.git']
  highest: any = []

  // Allow access to vuex getters
  repoRelations!: any;
  repos!: any;
  repoGroups!:any;
  apiRepos!:any;
  apiGroups!:any;
  cache!:any;

  // Allow access to vuex actions
  loadRepoGroups!:any;
  loadRepos!:any;
  createAPIObjects!:any;
  endpoint!:any;
  addRepoGroup!:any;

  // 'created' lifecycle hook
  // Gets ran on component initialization, data collection should be handled here
  created () {

    // Load the data we need
    this.loadRepoGroups().then((groups: any) => {
    //   this.loadRepos().then(() => {
        // Creating AugurAPI objects for the entities we will query
        // for (let n = 0; n < 3; n++){
        //   let group = this.repoGroups[n]
        //   let relatedRepos:any[] = []
        //   for (let i = 0; i < this.desiredReposPerGroup && Object.keys(this.repoRelations[group.rg_name]).length > i; i++) {
        //     relatedRepos.push(this.repoRelations[group.rg_name][Object.keys(this.repoRelations[group.rg_name])[i]])
        //   }
        //   this.createAPIObjects({groups: [group], repos: relatedRepos})
        //   // Spark data
        //   let sparkRepos:any[] = []
        //   relatedRepos.forEach((repo:any) => {
        //     sparkRepos.push(this.apiRepos[repo.url])
        //   })
        // }
      let relevantApiGroups: any[] = []
      let addingGroupPromises: any[] = []
      groups.forEach((group: any) => {
        addingGroupPromises.push(this.addRepoGroup(group))
      })
      Promise.all(addingGroupPromises).then((groups) => {
        groups.forEach((group) => {
          relevantApiGroups.push(this.apiGroups[group.rg_name])
        })
        
      
        this.endpoint({repoGroups: relevantApiGroups, endpoints: ['topInsights']}).then((tuples:any) => {
          groups.forEach((group) => {
            if ('topInsights' in tuples[group.rg_name].groupEndpoints){
              tuples[group.rg_name].groupEndpoints.topInsights.forEach((tuple:any) => {
                // tuple.value = +tuple.value
                let i = 0

                this.highest.forEach((record:any) => {
                  if ((tuple.date > record.date && tuple.rg_name == record.rg_name)){
                    console.log('hihihi')
                    this.highest[i] = tuple
                  }
                  i++
                })
                if (this.highest.length < 3 && (this.highest.length == 0 || this.highest[this.highest.length-1].rg_name != tuple.rg_name)) {
                  this.highest.push(tuple)
                }
                
                if (this.insights[group.rg_name]){
                  if (this.insights[group.rg_name][tuple.repo_git]) {
                    if (this.insights[group.rg_name][tuple.repo_git][tuple.ri_metric]) {
                      this.insights[group.rg_name][tuple.repo_git][tuple.ri_metric].push(tuple)
                    } else {
                      this.insights[group.rg_name][tuple.repo_git][tuple.ri_metric] = [tuple]
                    } 
                  } else {
                    this.insights[group.rg_name][tuple.repo_git] = {}
                    this.insights[group.rg_name][tuple.repo_git][tuple.ri_metric] = [tuple]
                  }
                } else {
                  this.insights[group.rg_name] = {}
                  this.insights[group.rg_name][tuple.repo_git] = {}
                  this.insights[group.rg_name][tuple.repo_git][tuple.ri_metric] = [tuple]
                }
              })
              
            } else {
              console.log("top insights did not load correctly")
            }
          })
          this.loadedInsights = true
          this.loadedRelations = true
        })
      })  
    //   })
    })
  }

  getOwner (url: string) {
    let first = url.indexOf(".")
    let last = url.lastIndexOf(".")
    let domain = null
    let owner = null
    let repo = null
    let extension = false
    if (url.includes("https://")){
      url = url.substr(8)
      console.log(url)
    }

    if (first == last) { //normal github
      domain = url.substring(0, first)
      owner = url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
      repo = url.slice(url.lastIndexOf('/') + 1)
      console.log(owner+ "/" + repo)
      return owner
    } else if (url.slice(last) == '.git') { //github with extension
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
  }

  getRepo (url: string) {
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
  }

  getDirection (values: any[]) {
    let i = 0
    for (i = 0; i < values.length; i++){
      if (values[i].discovered){
        break
      }
    }
    if (values[i+1].value > values[i].value) 
      return 'arrow_upward'
    else
      return 'arrow_downward'
  }

  date_diff_indays (date1: any, date2: any) {
    let dt1 = new Date(date1);
    let dt2 = new Date(date2);
    return Math.floor((Date.UTC(dt2.getFullYear(), dt2.getMonth(), dt2.getDate()) - Date.UTC(dt1.getFullYear(), dt1.getMonth(), dt1.getDate()) ) /(1000 * 60 * 60 * 24));
  }

  getPhrase (values: any[]) {
    let i = 0
    let date = Date.now()
    console.log(date)
    for (i = 0; i < values.length; i++){
      if (values[i].discovered){
        date = this.date_diff_indays(values[i].date, date)
        break
      }
    }
    this.timeframes[values[0].repo_git] = date + ' days'
    if (values[i+1].value > values[i].value) 
      return 'increase in ' + values[0].ri_metric + ' within the past ' + date + ' days'
    else
      return 'decrease in ' + values[0].ri_metric + ' within the past ' + date + ' days'
  }

  onGitRepo (e: any) {
    this.$router.push({
      name: 'repo_overview',
      params: {group:e.rg_name, repo:e.repo_name, repo_group_id: e.repo_group_id, repo_id: e.repo_id}
    })
  }

  onInspectInsight (e: any) {
    console.log(e[0])
    this.$router.push({
      name: 'inspect_insight',
      params: {'rg_name': e[0].rg_name, 'repo_git': e[0].repo_git, 'ri_metric': e[0].ri_metric}
    })
  }


}
</script>


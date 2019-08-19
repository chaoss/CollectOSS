<template>
  <d-container fluid class="main-content-container px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="page-title" style="font-size: 1rem">Insights</h3>
      </div>
    </div>

    <div class="row" style="transform: translateX(1rem)">
      <div class="row col col-9">
        <d-card class="card-small h-100" style="height:45% !important; margin-bottom:1rem">

          <!-- Card Header -->
          <d-card-header class="border-bottom">
            <h6 class="m-0">{{ getRepo }}</h6>
            <div class="block-handle"></div>
          </d-card-header>

          <d-card-body class="pt-0">
            <!-- <d-row class="border-bottom py-2 bg-light">

              <d-col col sm="6" class="d-flex mb-2 mb-sm-0">
                <d-input-group size="sm" class="date-range d-flex justify-content-left">
                  <d-datepicker v-model="dateRange.from" :highlighted="{ from: dateRange.from, to: dateRange.to || new Date() }" placeholder="Start Date" typeable small />
                  <d-datepicker v-model="dateRange.to" :highlighted="{ from: dateRange.from, to: dateRange.to || new Date() }" placeholder="End Date" typeable small />
                  <d-input-group-text slot="append">
                    <i class="material-icons">&#xE916;</i>
                  </d-input-group-text>
                </d-input-group>
              </d-col>

              <d-col col sm="6">
                <d-button size="sm" class="d-flex btn-white ml-auto mr-auto ml-sm-auto mr-sm-0 mt-3 mt-sm-0">View Full Report &rarr;</d-button>
              </d-col>

            </d-row> -->

            <!-- Main insight -->
            <div v-if="!loadedInsights" style="padding: 3.5rem 0 0 3.7rem;" class="col-md-8 col-lg-9">

              <spinner style="padding: 1rem 0 1rem 0; position: relative; transform: translateY(-40%);"></spinner>
            </div>
            <main-insight v-if="loadedInsights"
              :data="values" :url="getRepo" color="black" source="main"
            ></main-insight>

          </d-card-body>
        </d-card>
        
        
        
        
      </div>

      <!-- sidebar of other repo groups -->
      <div class="row col col-3" style="transform: translateX(3rem)">
        <div class="col-12 page-header row no-gutters py-4">
          <div class="col-12 text-center text-sm-left mb-0">
            <h3 class="page-title" style="font-size: 1rem">View insights for other repo groups</h3>
          </div>
        </div>
        <d-col v-if="loadedInsights" v-for="(group, idx) in Object.keys(insights).slice(0,6)" :key="idx" lg="12" sm="12" class="mb-4">
          <d-card class="card-small card">
            <div class="border-bottom card-header">
              <h6 class="m-0">{{ group }}</h6>
              <div class="block-handle"></div>
            </div>
            <div class="p-0 card-body">
              <div class="list-group-small list-group list-group-flush">
                <div v-for="(repo, i) in Object.keys(insights[group]).slice(0,5)" class="d-flex px-3 list-group-item" style="text-align: left">
                  <a href="#" @click="onInspectInsight(insights[group][repo][Object.keys(insights[group][repo]).slice(0,1)[0]])">
                    <span class="text-semibold text-fiord-blue" style="font-size: .65rem; padding: 0">{{ repo }}</span>
                  </a>
                  <div v-if="loadedInsights" v-for="metric in Object.keys(insights[group][repo]).slice(0,1)" style="margin: 0 0 0 auto; float:right">
                    <spark-chart :color="colors[idx]" :url="repo" :data="insights[group][repo][metric]" style="max-height: 50px; padding-bottom: 0px; transform:translateX(-1rem)"/>
                  </div>
                  
                </div>
              </div>
            </div>
          </d-card>
        </d-col>
        
      </div>
      <!-- Others for this repo -->
        
      <d-row class="col-12" style="transform: translateY(-28rem); padding: 0 !important;">
        <div class="col-12 page-header row no-gutters py-4">
          <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
            <h3 class="page-title" style="font-size: 1rem">View other top insights</h3> <!-- insights for this repo -->
          </div>
        </div>
        <div v-if="!loadedInsights" class="col-md-4 col-lg-3">
          <spinner style="padding: 1.5rem 0 1rem 0; position: relative; transform: translateY(-50%);"></spinner>
        </div>

        <d-col v-if="loadedInsights" v-for="(group, idx) in Object.keys(insights).slice(0,3)" :key="idx" lg="3" md="4" sm="8" class="mb-4">
          
          <d-card v-if="idx < 4" v-for="repo in Object.keys(insights[group]).slice(0,1)" class="card-small card-post card-post--1">
            <div class="card-post__image" v-for="metric in Object.keys(insights[group][repo]).slice(0,1)">
              <d-badge pill :class="['card-post__category', 'bg-' + themes[idx] ]">{{ group }}</d-badge>
              <insight-chart style="transform: translateX(-3.35rem)" :data="insights[group][repo][metric]" :url="repo" :color="colors[idx]"></insight-chart>

              <div class="card-post__author d-flex">
                <a href="#" :style="colors[idx]" class="card-post__author-avatar card-post__author-avatar--small" style="text-indent: 0; text-align: center; font-size: 1rem">
                  <i class="material-icons" style="position: relative; top: 50%; transform: translateY(-60%)">{{ getDirection(insights[group][repo][metric]) }}</i>
                </a>
              </div>
            </div>
            <d-card-body v-for="metric in Object.keys(insights[group][repo]).slice(0,1)">
              <h5 class="card-title">
                <a href="#" @click="onInspectInsight(insights[group][repo][metric])" class="text-fiord-blue">{{ repo.substr(19) }}</a>
              </h5>
              <p class="card-text d-inline-block mb-1" style="font-size: .75rem">This repository had a sharp {{ getPhrase(insights[group][repo][metric]) }}</p>
              <span class="text-muted" style="font-size: .75rem">1 month</span>
            </d-card-body>
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
import MainInsight from '../components/charts/MainInsight.vue';
import Spinner from '../components/Spinner.vue';

@Component({
  methods: {
    ...mapActions('common',[
      'loadRepos',
      'loadRepoGroups',
      'createAPIObjects',
      'endpoint',
      'addRepoGroup',
      'addRepo'
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

  },
  components: {
    SparkChart,
    InsightChart,
    Spinner,
    MainInsight
  }
})
export default class InspectInsight extends Vue {
  
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
  values: any = []
  test: any[] = ['https://github.com/rails/ruby-coffee-script.git', 'https://github.com/Comcast/Hygieia.git','https://github.com/apache/jclouds-site.git',
    'https://github.com/apache/karaf-jclouds.git', 'https://github.com/openssl/openssl', 'https://github.com/rails/ruby-coffee-script.git']
  dateRange: any = {
    from: null,
    to: null,
  }
  addedRepo:boolean = false

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
  addRepo!:any;

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
        console.log(groups)
        groups.forEach((group) => {
          relevantApiGroups.push(this.apiGroups[group.rg_name])
        })
        
      
        this.endpoint({repoGroups: relevantApiGroups, endpoints: ['topInsights']}).then((tuples:any) => {          
          groups.forEach((group) => {
            if ('topInsights' in tuples[group.rg_name].groupEndpoints){
              tuples[group.rg_name].groupEndpoints.topInsights.forEach((tuple:any) => {
                // tuple.value = +tuple.value
                if (tuple.repo_git == this.getRepo && !this.addedRepo){
                  this.addedRepo = true
                  this.addRepo(tuple).then((repo:any) => {
                    console.log("added main repo: ", repo)
                    repo[this.apiMetric]().then((values: any) => {
                      console.log("hit endpoint for repo", this.apiMetric, values)
                      this.values = values
                    }).catch(function () {
                      console.log("Promise Rejected");
                    });
                  })
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

  get getRepo() {
    return this.$route.params.repo_git
  }

  get getMetric() {
    return this.$route.params.ri_metric
  }

  get apiMetric() {
    if (this.$route.params.ri_metric == 'New Issues (issues)'){
      return 'issueNew'
    } else if (this.$route.params.ri_metric == 'Code Changes'){
      return 'codeChanges'
    } else if (this.$route.params.ri_metric == 'Code Changes Lines'){
      return 'codeChangesLines'
    }
    return ''
  }

  get getGroup() {
    return this.$route.params.rg_name
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


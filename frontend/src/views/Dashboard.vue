<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-container fluid class="main-content-container px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <!-- <span class="text-uppercase page-subtitle">Viewing all</span> -->
        <h3 class="dashboardHeader page-title">Most Anomalous Insights Across Your Repos</h3>
      </div>
    </div>

    <!-- First Row of Posts -->

        <d-row>
          
          <d-col v-for="(record, idx) in highest_frame" :key="idx" lg="4" md="4" sm="6" class="mb-4">
            
            <d-card v-if="idx < highest_frame.length" class="card-small card-post card-post--1">

              <div class="dashboardDiv" v-if="!loadedInsights">
                <spinner class="dashboardSpinner"></spinner>
              </div>

              <div class="card-post__image" v-if="loadedInsights">
                <d-badge pill :class="['card-post__category', 'bg-' + (color_mapping[highest[idx].ri_metric].theme || 'info') ]">{{ highest[idx].ri_metric }} ({{ highest[idx].ri_field }})</d-badge>
                <insight-chart style="" :data="insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric]" :url="highest[idx].repo_git" :color="color_mapping[highest[idx].ri_metric].hex || '#FFC107'"></insight-chart>

                <!-- <div class="card-post__author d-flex">
                  <a href="#" :style="color_mapping[highest[idx].ri_metric].hex" class="card-post__author-avatar card-post__author-avatar--small dashboardDiv2">
                    <i class="material-icons dashboardI">{{ getDirection(insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric]) }}</i>
                  </a>
                </div> -->
              </div>

              <d-card-body v-if="loadedInsights">
                <h5 class="card-title">
                  <a :id="idx" href="#" @click="onGitRepo(highest[idx])" class="text-fiord-blue underline">{{ highest[idx].repo_git.substr(19) }}</a>
                  <d-tooltip 
                    :target="'#' + idx"
                    container=".shards-demo--example--tooltip-01"
                    placement="right"
                    offset="10">
                    Click here to see an overview of this repository's metrics
                  </d-tooltip>
                </h5>
                <p class="card-text d-inline-block mb-1 dashboardP">This repository had {{ getPhrase(insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric]) }}</p>
                <d-row>
                  <d-col cols="12" sm="5">
                    <d-row>
                      <d-col cols="12" sm="12">
                        <d-button 
                        :id="'ev' + idx" 
                        size="sm" 
                        @click="onGitRepo(insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric][0])" 
                       
                        class="dashboardButton d-flex btn-white ml-auto mr-auto ml-sm-auto mr-sm-0 mt-3 mt-sm-0">Evolution &rarr;</d-button>
                        <d-tooltip 
                          :target="'#ev' + idx"
                          container=".shards-demo--example--tooltip-01"
                          offset="20">
                          Click to see evolution metrics for this repo.
                        </d-tooltip>
                      </d-col>
                      
                      <!-- <d-col cols="12" sm="12">
                        <span class="text-muted dashboardP">{{ timeframes[highest[idx].repo_git] }}</span>
                      </d-col>
                      <p></p>
                      <d-col cols="12" sm="12">
                        <d-button 
                        theme="info" size="sm" 
                        :id="'inspect' + idx" 
                        @click="onInspectInsight(insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric][0])" 
                        class="dashboardButton d-flex btn-white ml-auto mr-auto ml-sm-auto mr-sm-0 mt-3 mt-sm-0">View Insight Details &rarr;</d-button>
                        <d-tooltip 
                          :target="'#inspect' + idx"
                          container=".shards-demo--example--tooltip-01"
                          placement="right"
                          offset="20">
                          Click to see more about this insight.
                        </d-tooltip>
                      </d-col> -->
                    </d-row>
                  </d-col>
                  <!-- View Full Report -->

                  <d-col cols="12" sm="7" class="dashboardCol">
                    <d-row>
                      

                      
                      <p></p>
                      <d-col cols="12" sm="12">
                        <d-button theme="secondary" :id="'ri' + idx" size="sm" @click="onRisk(insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric][0])" class="dashboardButton d-flex btn-white ml-auto mr-auto ml-sm-auto mr-sm-0 mt-3 mt-sm-0">Risk &rarr;</d-button>
                        <d-tooltip 
                          :target="'#ri' + idx"
                          container=".shards-demo--example--tooltip-01"
                          placement="right"
                          offset="20">
                          Click to see risk metrics for this repo.
                        </d-tooltip>
                      </d-col>
                      
                    </d-row>
                  </d-col>
                </d-row>
              </d-card-body>
            </d-card>
          </d-col>
        </d-row>



        <!-- grouped by repo group, remove for now bc confusion w difference of scope -->

        <!--
        <div style="transform: translateY(-0px)">
          <div class="page-header row no-gutters py-4">
            <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
              <h3 style="font-size: 1rem" class="page-title">5 Most Anomalous Insights Across All Your Repo Groups</h3>
            </div>
          </div>
          
           <d-row>
            <d-col v-if="!loadedInsights">
              <d-card>
                <div style="">
                  <spinner></spinner>
                </div>
              </d-card>
            </d-col>

            <d-col v-else v-for="(group, idx) in Object.keys(insights).slice(0,6)" :key="idx" lg="4" sm="12" class="mb-4">
              <d-card class="card-small card">
                <div class="border-bottom card-header">
                  
                  <div v-for="repo in Object.keys(insights[group]).slice(0,1)">
                    <div v-for="metric in Object.keys(insights[group][repo]).slice(0,1)">
                        <h6 class="m-0" style="color: black">{{ group }}</h6>
                    </div>
                  </div>

                  <div class="block-handle">
                    <div v-for="repo in Object.keys(insights[group]).slice(0,1)">
                      <div v-for="metric in Object.keys(insights[group][repo]).slice(0,1)">
                        <d-button size="sm" @click="onRepoGroup(insights[group][repo][metric][0])" style="color: white !important;margin-left: 0 !important;margin-top: 0.3rem !important;" class="d-flex btn-white ml-auto mr-auto ml-sm-auto mr-sm-0 mt-3 mt-sm-0">See all repos in this group &rarr;</d-button>
                      </div>
                    </div>
                  </div>

                </div>
                <div class="p-0 card-body">
                  <div class="list-group-small list-group list-group-flush">
                    <div v-for="(repo, i) in Object.keys(insights[group]).slice(0,5)" class="d-flex px-3 list-group-item" style="text-align: left">
                      <a :id="repo" href="#" class="underline text-semibold text-fiord-blue" style="width:100%" @click="onInspectInsight(insights[group][repo][Object.keys(insights[group][repo]).slice(0,1)[0]][0])">
                        <d-row>
                          <d-col style="max-width:10rem" lg="6" md="6" sm="6">
                            <span class="" style="font-size: 1rem; padding: 0;">{{ getRepo(repo) }}</span>
                          </d-col>
                          <d-col v-if="loadedInsights" lg="6" md="6" sm="6" v-for="metric in Object.keys(insights[group][repo]).slice(0,1)" style="margin: 0 0 0 auto; float:right">
                            <spark-chart :color="colors[idx]" :title="metric + ' (' + insights[group][repo][metric][0].ri_field + ')'" :url="repo" :data="insights[group][repo][metric]" style="max-height: 50px; padding-bottom: 0px; "/>
                          </d-col>
                        </d-row>
                      </a>
                      <d-tooltip 
                        :target="'#' + repo"
                        container=".shards-demo--example--tooltip-01"
                        placement="right"
                        offset="10">
                        This repository had a sharp {{ getPhrase(insights[group][repo][Object.keys(insights[group][repo]).slice(0,1)]) }}. Click to see more about this insight.
                      </d-tooltip>
                    </div>
                  </div>
                </div>
              </d-card>
            </d-col>
          </d-row> -->
        <!-- </div> -->
  </d-container>
</template>

<script lang="ts">
import { mapActions, mapGetters, mapMutations } from "vuex";
import Component from 'vue-class-component';
import Vue from 'vue';


import SparkChart from '../components/charts/SparkChart.vue';
import InsightChart from '../components/charts/InsightChart.vue';
import Spinner from '../components/Spinner.vue';

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
    ]),
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
  // colors: string[] = ["#24a2b7", "#FF3647","#159dfb", "#FFC107", '343a40'];
  color_mapping: any = {
    'code-changes': { 'hex': "#FFC107", 'theme': 'warning' },
    'code-changes-lines': { 'hex': "#FF3647", 'theme': 'danger' },
    'issues-new': { 'hex': "#159dfb", 'theme': 'royal-blue' },
    'reviews': { 'hex': '#343a40', 'theme': 'dark' },
    'contributors-new': { 'hex': "#FFC107", 'theme': 'warning' }
  }
  // themes: string[] = ['info', 'danger','royal-blue', 'warning', 'dark'];
  loadedInsights: boolean = false
  desiredReposPerGroup: number = 5
  desiredTopInsights: number = 12
  insights: any = {}
  timeframes: any = {}
  test: any[] = ['https://github.com/rails/ruby-coffee-script.git', 'https://github.com/Comcast/Hygieia.git','https://github.com/apache/jclouds-site.git',
    'https://github.com/apache/karaf-jclouds.git', 'https://github.com/openssl/openssl', 'https://github.com/rails/ruby-coffee-script.git']
  highest_frame: any = [{}, {}, {}, {}, {}, {}]
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

      let relevantApiGroups: any[] = []
      let addingGroupPromises: any[] = []
      groups.forEach((group: any) => {
        addingGroupPromises.push(this.addRepoGroup(group))
      })

      Promise.all(addingGroupPromises).then((groups: any) => {
        this.highest_frame = []
        let dupesAllowed = this.desiredTopInsights - groups.length
        let count = 0
        groups.forEach((group: any) => {
          if (count < 12)
            this.highest_frame.push({})
          relevantApiGroups.push(this.apiGroups[group.rg_name])
          count += 1
        })

        this.endpoint({repoGroups: relevantApiGroups, endpoints: ['topInsights']}).then((tuples: any) => {
          groups.forEach((group: any) => {
            console.log("Group tuples: ", tuples[group.rg_name].groupEndpoints.topInsights)
            if ('topInsights' in tuples[group.rg_name].groupEndpoints){
              let n = null
              for (n = 0; n < tuples[group.rg_name].groupEndpoints.topInsights.length; n++) {
              // tuples[group.rg_name].groupEndpoints.topInsights.forEach((tuple:any) => {

                let tuple = tuples[group.rg_name].groupEndpoints.topInsights[n]

                let i = 0
                let alreadyIncluded = false


                this.highest.forEach((record:any) => {
                  // console.log(record.repo_git, tuple.repo_git)
                  if (record.repo_git == tuple.repo_git || record.repo_id == tuple.repo_id)
                    alreadyIncluded = true
                })


                for (let i = 0; i < this.highest.length; i++) {
                  if (tuple.date > this.highest[i].date && !alreadyIncluded && this.highest.length >= this.desiredTopInsights){ 
                    
                    if (tuples[group.rg_name].groupEndpoints.topInsights[n + 1] && tuples[group.rg_name].groupEndpoints.topInsights[n - 1]) {
                      if (tuples[group.rg_name].groupEndpoints.topInsights[n + 1].repo_git == tuple.repo_git || tuples[group.rg_name].groupEndpoints.topInsights[n - 1].repo_git == tuple.repo_git) {
                        console.log("Update hightest condition met: ", tuple)
                        this.highest[i] = tuple
                        break
                      }
                    }
                  }
                }
                //if (this.highest.length < this.desiredTopInsights && (this.highest.length == 0 || this.highest[this.highest.length - 1].rg_name != tuple.rg_name || dupesAllowed > 0 && !alreadyIncluded)) {
                if (this.highest.length < this.desiredTopInsights && !alreadyIncluded) {
                  if (tuples[group.rg_name].groupEndpoints.topInsights[n + 1] && tuples[group.rg_name].groupEndpoints.topInsights[n - 1]) {
                    if (tuples[group.rg_name].groupEndpoints.topInsights[n + 1].repo_git == tuple.repo_git || tuples[group.rg_name].groupEndpoints.topInsights[n - 1].repo_git == tuple.repo_git) {
                      dupesAllowed--
                      console.log("Set hightest condition met: ", tuple)
                      this.highest.push(tuple)
                    }
                  }
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
              }
              this.highest_frame = this.highest

              
            } else {
              console.log("top insights did not load correctly")
            }
          })
          console.log("check:",this.insights, JSON.stringify(this.highest[0]))
          this.loadedInsights = true
        }).catch((e: any) => {
          console.log("Error occurred top insights for all repo groups: ",e)
        })
      }).catch((e: any) => {
        console.log("Error occurred adding repo groups: ",e)
      })
    }).catch((e: any) => {
      console.log("Error occurred loading repo groups on Dashboard level: ",e)
    })

    for (let i = 0; i < this.highest.length; i++) {
      if (!this.color_mapping[this.highest[i].ri_metric])
        this.highest.splice(i, 1)
    }
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
    if (values[i+1]){
      if (values[i+1].value > values[i].value) 
        return 'arrow_upward'
      else
        return 'arrow_downward'
    } else {
      return '-'
    }
      
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
    this.timeframes[values[0].repo_git] = date + ' days ago'
    if (values[i+1]){
      if (values[i+1].value > values[i].value) 
        return 'a sharp increase in ' + values[0].ri_metric + ' ' + date + ' days ago'
      else
        return 'a sharp decrease in ' + values[0].ri_metric + ' ' + date + ' days ago'
    }
    else {
      return 'an anomaly in ' + values[0].ri_metric + ' ' + date + ' days ago'
    }
  }

  onGitRepo (e: any) {
    console.log("onGitRepo: ",e)
    this.$router.push({
      name: 'repo_overview',
      params: {'group':e.rg_name, 'repo':e.repo_git, 'repo_group_id': e.repo_group_id, 'repo_id': e.repo_id}
    })
  }

  onRisk (e: any) {
    console.log("onRisk: ",e)
    this.$router.push({
      name: 'repo_risk',
      params: {'group':e.rg_name, 'repo':e.repo_git, 'repo_group_id': e.repo_group_id, 'repo_id': e.repo_id}
    })
  }

  onInspectInsight (e: any) {
    console.log("onInspectInsight: ",e)
    this.$router.push({
      name: 'inspect_insight',
      params: {'group': e.rg_name, 'repo': e.repo_git, 'repo_group_id': e.repo_group_id, 'repo_id': e.repo_id, 'metric': e.ri_metric}
    })
  }

  onRepoGroup (e: any) {
    console.log("onRepoGroup: ",e)
    this.$router.push({
      name: 'group_overview',
      params: {'group':e.rg_name, 'repo':e.repo_git, 'repo_group_id': e.repo_group_id, 'repo_id': e.repo_id}
    })
  }


}
</script>

<style scoped>
.card-post__image {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: column;
}
</style>

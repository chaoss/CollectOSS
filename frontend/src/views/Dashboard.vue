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
          
          <d-col v-for="(record, idx) in highest_frame" :key="idx" lg="4" md="4" sm="6" class="mb-4">
            
            <d-card v-if="idx < highest_frame.length" class="card-small card-post card-post--1">

              <div v-if="!loadedInsights">
                <spinner style="padding: 1rem 0 1rem 0; position: relative; transform: translateY(-50%);"></spinner>
              </div>

              <div class="card-post__image" v-if="loadedInsights">
                <d-badge pill :class="['card-post__category', 'bg-' + themes[idx] ]">{{ highest[idx].ri_metric }} ({{ highest[idx].ri_field }})</d-badge>
                <insight-chart style="" :data="insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric]" :url="highest[idx].repo_git" :color="colors[idx]"></insight-chart>

                <div class="card-post__author d-flex">
                  <a href="#" :style="colors[idx]" class="card-post__author-avatar card-post__author-avatar--small" style="text-indent: 0; text-align: center; font-size: 1rem">
                    <i class="material-icons" style="position: relative; top: 50%; transform: translateY(-60%)">{{ getDirection(insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric]) }}</i>
                  </a>
                </div>
              </div>

              <d-card-body v-if="loadedInsights">
                <h5 class="card-title">
                  <a href="#" @click="onGitRepo(highest[idx])" class="text-fiord-blue underline">{{ highest[idx].repo_git.substr(19) }}</a>
                </h5>
                <p class="card-text d-inline-block mb-1" style="font-size: .75rem">This repository had a sharp {{ getPhrase(insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric]) }}</p>
                <d-row>
                  <d-col cols="12" sm="5"><span class="text-muted" style="font-size: .75rem">{{ timeframes[highest[idx].repo_git] }}</span></d-col>
                  <!-- View Full Report -->
                  <d-col cols="12" sm="7" style="transform: translateX(-1rem) !important;">
                    <d-button size="sm" @click="onInspectInsight(insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric])" style="color: white !important" class="d-flex btn-white ml-auto mr-auto ml-sm-auto mr-sm-0 mt-3 mt-sm-0">View Full Report &rarr;</d-button>
                  </d-col>
<!--                   <div class="col col-7"><span class="text-muted" style="font-size: .75rem"><a href="#" class="text-fiord-blue" @click="onInspectInsight(insights[highest[idx].rg_name][highest[idx].repo_git][highest[idx].ri_metric])">See more here...</a></span></div>
 -->            </d-row>
              </d-card-body>
            </d-card>
          </d-col>
        </d-row>

        <div style="transform: translateY(-0px)">
          <div class="page-header row no-gutters py-4" style="padding-top: 5 !important;">
            <div class="col-12 col-sm-6 text-center text-sm-left mb-0">
              <!-- <span class="text-uppercase page-subtitle">Components</span> -->
              <h3 class="page-title" style="font-size: 1rem">Top 5 Most Significant Anomalies In Your Repo Groups</h3>
            </div>
          </div>

          <!-- Second Row of Posts -->
          
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
                      <!-- <a href="#" @click="onRepoGroup(insights[group][repo][metric][0])"> -->
                        <h6 class="m-0" style="color: black">{{ group }}</h6>
                      <!-- </a> -->
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
                      <a href="#" style="max-width:10rem" @click="onGitRepo(insights[group][repo][Object.keys(insights[group][repo]).slice(0,1)[0]][0])">
                        <span class="text-semibold text-fiord-blue underline" style="font-size: 1rem; padding: 0">{{ getRepo(repo) }}</span>
                      </a>
                      <div v-if="loadedInsights" v-for="metric in Object.keys(insights[group][repo]).slice(0,1)" style="margin: 0 0 0 auto; float:right">
                        <spark-chart :color="colors[idx]" :title="metric + ' (' + insights[group][repo][metric][0].ri_field + ')'" :url="repo" :data="insights[group][repo][metric]" style="max-height: 50px; padding-bottom: 0px; "/>
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
  colors: string[] = ["#24a2b7", "#FF3647","#159dfb", "#FFC107","#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"];
  tempInsightEndpoints: string[] = ['issuesClosed', 'codeChangesLines', 'issueNew'];
  tempInsightRepos: any[] = [];
  tempInsightTimeframes: string[] = ['past 1 month', 'past 3 months', 'past 2 weeks'];
  themes: string[] = ['info', 'danger','royal-blue', 'warning', 'dark'];
  loadedInsights: boolean = false
  desiredReposPerGroup: number = 5
  insights: any = {}
  timeframes: any = {}
  test: any[] = ['https://github.com/rails/ruby-coffee-script.git', 'https://github.com/Comcast/Hygieia.git','https://github.com/apache/jclouds-site.git',
    'https://github.com/apache/karaf-jclouds.git', 'https://github.com/openssl/openssl', 'https://github.com/rails/ruby-coffee-script.git']
  highest_frame: any = [{},{},{}]
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
        groups.forEach((group: any) => {
          relevantApiGroups.push(this.apiGroups[group.rg_name])
        })
        this.endpoint({repoGroups: relevantApiGroups, endpoints: ['topInsights']}).then((tuples: any) => {
          groups.forEach((group: any) => {
            console.log("Group tuples: ", tuples[group.rg_name].groupEndpoints.topInsights)
            if ('topInsights' in tuples[group.rg_name].groupEndpoints){
              tuples[group.rg_name].groupEndpoints.topInsights.forEach((tuple:any) => {
                // tuple.value = +tuple.value
                let i = 0
                let alreadyIncluded = false


                this.highest.forEach((record:any) => {
                  console.log(this.highest[i], Object.keys(this.highest[i]).length == 0)
                  if ((tuple.date > record.date && tuple.rg_name == record.rg_name)){
                    console.log("Update hightest condition met: ", tuple)
                    this.highest[i] = tuple
                  }
                  i++
                })
                if (this.highest.length < 3 && (this.highest.length == 0 || this.highest[this.highest.length-1].rg_name != tuple.rg_name) && tuple.repo_git) {
                  console.log("Set hightest condition met: ", tuple)
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
    this.timeframes[values[0].repo_git] = date + ' days'
    if (values[i+1]){
      if (values[i+1].value > values[i].value) 
        return 'increase in ' + values[0].ri_metric + ' within the past ' + date + ' days'
      else
        return 'decrease in ' + values[0].ri_metric + ' within the past ' + date + ' days'
    }
    else {
      return 'insight in ' + values[0].ri_metric + ' within the past ' + date + ' days'
    }
  }

  onGitRepo (e: any) {
    console.log(e)
    this.$router.push({
      name: 'repo_overview',
      params: {'group':e.rg_name, 'repo':e.repo_git, 'repo_group_id': e.repo_group_id, 'repo_id': e.repo_id}
    })
  }

  onInspectInsight (e: any) {
    console.log(e[0])
    this.$router.push({
      name: 'inspect_insight',
      params: {'rg_name': e[0].rg_name, 'repo_git': e[0].repo_git, 'ri_metric': e[0].ri_metric}
    })
  }

  onRepoGroup (e: any) {
    console.log(e)
    this.$router.push({
      name: 'group_overview',
      params: {'group':e.rg_name, 'repo':e.repo_git, 'repo_group_id': e.repo_group_id, 'repo_id': e.repo_id}
    })
  }


}
</script>


<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-container fluid class="main-content-container px-4">

    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <span class="text-uppercase page-subtitle">Viewing all</span>
        <h3 class="page-title">Workers</h3>
      </div>
    </div>


    <div class="row">
      <div class="col">
        <div class="card card-small mb-4">
          <div class="card-header border-bottom">
            <h6 class="m-0">Currently Implemented Data Collection Workers</h6>
          </div>
          <div class="card-body p-0 pb-3 text-center">
            <table class="workersTable table mb-0">
              <thead class="bg-light">
                <tr>
                  <th scope="col" class="border-0" v-on:click="sortTable('url')"> 
                    Worker Name/Type
                    
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_name')"> 
                    Status
                   
                  </th>
                  <!-- <th width="30%" scope="col" class="border-0" v-on:click="sortTable('description')">
                    <div class="row">
                      <div class="col col-9">Repo Description</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'description' == sortColumn"></div>
                    </div>
                  </th> -->
                  <!-- <th scope="col" class="border-0">Options</th> -->
                </tr>
              </thead>
              <tbody>
                <tr v-for="(worker,index) in workers" v-bind:item="worker">
                  <td>
                    <a href="#">{{ worker.name }}</a>
                  </td>
                  <td>{{ worker.status }}</td>
                  <!-- <td>{{ repo.description }}</td> -->
                  <!-- <td>
                    <div class="row">
                      <button :id="'favorite'+index" class="nav-link col col-2" style="margin-left: 2rem; margin-right: 1rem; padding: 0;border: none; background: none;">
                        <i class="material-icons" style="color:#007bff;">star_rate</i>
                        <div class="item-icon-wrapper"></div>
                      </button>
                      <d-tooltip :target="'#favorite'+index"
                                 container=".shards-demo--example--tooltip-01">
                        Consider this repo group as a "favorite" and our workers will regulaly update its metrics' data before others
                      </d-tooltip>
                      <button :id="'add_compare'+index" class="nav-link col col-2" style="padding: 0;border: none; background: none;">
                        <i class="material-icons" style="color:#007bff;">library_add</i>
                        <div class="item-icon-wrapper"></div>
                      </button>
                      <d-tooltip :target="'#add_compare'+index"
                                 :triggers="['hover']"
                                 container=".shards-demo--example--tooltip-01">
                        Add this worker to your current compared repos
                      </d-tooltip>
                    </div>
                  </td> -->
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </d-container>
</template>

<script lang="ts">
import Component from 'vue-class-component';
import Vue from 'vue';
import {mapActions, mapGetters, mapMutations} from "vuex";
import Spinner from '../components/Spinner.vue'
@Component({
  components: {
    Spinner,
  },
  methods: {
    ...mapActions('common',[
      'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                  // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
      'getRepoRelations',
      'loadRepos',
      'addRepo'
    ]),

    ...mapActions('compare',[
      'addComparedRepo',
      'setBaseRepo'
    ])
  },
  computed: {
    ...mapGetters('common', [
      'sortedRepos'
    ]),
  },
})

export default class Workers extends Vue{
  colors: string[] = ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"];
  // repos: any[] = [];
  repo_groups:any[] = [];
  repo_relations:any[] =  [];
  themes: string[] = ['dark', 'info', 'royal-blue', 'warning'];
  loadedGroups: boolean = false;
  loadedSparks: boolean = false;
  loadedRepos: boolean = false;

  ascending:boolean = false;
  sortColumn: string ='name';

  workers:any[] = [
    {'name':'Issue Collection', 'status':'operational'},
    {'name':'Commit Analysis', 'status':'operational'},
    {'name':'Pull Request Analysis', 'status':'operational'},
    {'name':'Repository Insights', 'status':'operational'},
    {'name':'Linux Foundation Core Infrastructure Badging', 'status':'operational'},
    {'name':'Repository Metadata', 'status':'operational'},
    {'name':'CHAOSS Metrics Release Information', 'status':'operational'}
  ]

  getRepoRelations!: any
  sortedRepos!:any
  loadRepos!:any;
  
  addRepo!:any;
  setBaseRepo!:any;
  addComparedRepo!:any;


  created() {
    this.workers = [
      {'name':'Issue Collection', 'status':'operational'},
      {'name':'Commit Analysis', 'status':'operational'},
      {'name':'Pull Request Analysis', 'status':'operational'},
      {'name':'Repository Insights', 'status':'operational'},
      {'name':'Linux Foundation Core Infrastructure Badging', 'status':'operational'},
      {'name':'Repository Metadata', 'status':'operational'},
      {'name':'CHAOSS Metrics Release Information', 'status':'operational'}
    ]
  }
  
  sortTable(col: string) {
      if (this.sortColumn === col) {
        this.ascending = !this.ascending;
      } else {
        this.ascending = true;
        this.sortColumn = col;
      }
  }

}

</script>


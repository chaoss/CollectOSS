<template>
  <div class="main-content-container container-fluid px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <span class="text-uppercase page-subtitle">Viewing all</span>
        <h3 class="page-title">Repos</h3>
      </div>
    </div>

    <!-- Default Light Table -->
    <spinner v-if="!loaded_repos"></spinner>

    <div v-if="loaded_repos"  class="row">
      <div class="col">
        <div class="card card-small mb-4">
          <div class="card-header border-bottom">
            <h6 class="m-0">Currently Stored Repos</h6>
          </div>
          <div class="card-body p-0 pb-3 text-center">
            <table style="table-layout:fixed;" class="table mb-0">
              <thead class="bg-light">
                <tr>
                  <th width="20%" scope="col" class="border-0" v-on:click="sortTable('url')"> 
                    <div class="row">
                      <div class="col col-9">URL</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'url' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_name')"> 
                    <div class="row">
                      <div class="col col-9">Repo Group Name</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'rg_name' == sortColumn"></div>
                    </div>
                  </th>
                  <th width="30%" scope="col" class="border-0" v-on:click="sortTable('description')">
                    <div class="row">
                      <div class="col col-9">Repo Description</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'description' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('repo_count')">
                    <div class="row">
                      <div class="col col-9">Group's Repo Count</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'repo_count' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('commits_all_time')">
                    <div class="row">
                      <div class="col col-9">Total Commit Count</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'commits_all_time' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('issues_all_time')">
                    <div class="row">
                      <div class="col col-0">Total Issue Count</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'issues_all_time' == sortColumn"></div>
                    </div>
                  </th>
                  <!-- <th scope="col" class="border-0" v-on:click="sortTable('repo_status')">
                    <div class="row">
                      <div class="col col-9">Status</div>
                      <div class="col col-2 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'repo_status' == sortColumn"></div>
                    </div>
                  </th> -->
                  <th scope="col" class="border-0">Options</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(repo,index) in sorted_repos(sortColumn,ascending)" v-bind:item="repo">
                  <td>
                    <a href="#" @click="onGitRepo(repo)">{{ repo.url }}</a>
                  </td>
                  <td>{{ repo.rg_name }}</td>
                  <td>{{ repo.description }}</td>
                  <td>{{ repo.repo_count }}</td>
                  <td>{{ repo.commits_all_time }}</td>
                  <td>{{ repo.issues_all_time }}</td>
                  <!-- <td>{{ repo.repo_status }}</td> -->
                  <td>
                    <div class="row">
                      <button :id="'favorite'+index" class="nav-link col col-2" style="margin-left: 2rem; margin-right: 1rem; padding: 0;border: none; background: none;">
                        <i class="material-icons" style="color:#007bff;">star_rate</i>
                        <div class="item-icon-wrapper"></div>
                      </button>
                      <d-tooltip :target="'#favorite'+index"
                                 container=".shards-demo--example--tooltip-01">
                        Consider this repo group as a "favorite" and our workers will regulaly update its metrics' data before others
                      </d-tooltip>
                      <button :id="'add_compare'+index" class="nav-link col col-2" style="padding: 0;border: none; background: none;" @click="addComparedRepo(repo)">
                        <i class="material-icons" style="color:#007bff;">library_add</i>
                        <div class="item-icon-wrapper"></div>
                      </button>
                      <d-tooltip :target="'#add_compare'+index"
                                 :triggers="['hover']"
                                 container=".shards-demo--example--tooltip-01">
                        Add this repo group to your current compared repos
                      </d-tooltip>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
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
    ...mapMutations('compare',[
      'setBaseRepo',
    ]),
    ...mapActions('compare',[
      'addComparedRepo',
    ])
  },
  computed: {
    ...mapGetters('common', [
      'groupsInfo',
      'sorted_repos',
      'loaded_repos'
    ]),
  },
})

export default class Repos extends Vue{
  colors: string[] = ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"];
  testEndpoints: string[] = ['issuesClosed', 'codeChangesLines', 'issueNew'];
  testTimeframes: string[] = ['past 1 month', 'past 3 months', 'past 2 weeks'];
  // repos: any[] = [];
  repo_groups:any[] = [];
  repo_relations:any[] =  [];
  themes: string[] = ['dark', 'info', 'royal-blue', 'warning'];
  loadedGroups: boolean = false;
  loadedSparks: boolean = false;
  // loadedRepos: boolean = false;
  ascending:boolean = false;
  sortColumn: string ='commits_all_time';
  groupsInfo!:any;
  getRepoRelations!: any
  sorted_repos!:any
  loadRepos!:any;
  loaded_repos!:boolean;
  addRepo!:any;
  setBaseRepo!:any;
  addComparedRepo!:any;


  created() {
    
    if (!this.loaded_repos) {
      this.loadRepos()
    }

  }
  
  sortTable(col: string) {
      if (this.sortColumn === col) {
        this.ascending = !this.ascending;
      } else {
        this.ascending = true;
        this.sortColumn = col;
      }
  }

  onGitRepo (e: any) {
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
      // this.$store.commit('setRepo', {
      //   gitURL: e.url
      // })

      this.setBaseRepo(e);

      this.addRepo(e);

      // this.$store.commit('setTab', {
      //   tab: 'git'
      // })

      this.$router.push({
        name: 'repo_overview',
        params: {owner:owner, repo:repo}
      })
  }
}

</script>



// ssdcript>
// export default {
//   components: {

//   },
//   computed: {
//   },
//   data() {
//     return {
//       colors: ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
//       testEndpoints: ['codeCommits', 'closedIssues', 'openIssues'],
//       testTimeframes: ['past 1 month', 'past 3 months', 'past 2 weeks'],
//       repos: [],
//       repo_groups: [],
//       repo_relations: {},
//       themes: ['dark', 'info', 'royal-blue', 'warning'],
//       loaded: false,
//       ascending: false,
//       sortColumn: '',
//       group_id_name_map: {},
//     }
//   },
//   methods: {
//     sortTable(col) {
//       if (this.sortColumn === col) {
//         this.ascending = !this.ascending;
//       } else {
//         this.ascending = true;
//         this.sortColumn = col;
//       }

//       var ascending = this.ascending;

//       this.repos.sort(function(a, b) {
//         if (a[col] > b[col]) {
//           return ascending ? 1 : -1
//         } else if (a[col] < b[col]) {
//           return ascending ? -1 : 1
//         }
//         return 0;
//       })
//     },
//     getRepoGroups() {
//       console.log("START")
//       window.AugurAPI.getRepos().then((data) => {
//         this.repos = data
//         console.log("LOADED repos", this.repos)
//         window.AugurAPI.getRepoGroups().then((data) => {
//           $(this.$el).find('.spinner').removeClass('loader')
//           $(this.$el).find('.spinner').removeClass('relative')
//           this.repo_groups = data
//           //move down between future relation endpoint
//           this.repo_groups.forEach((group) => {
//             this.repo_relations[group.rg_name] = this.repos.filter(function(repo){
//               return repo.rg_name == group.rg_name
//             })
//             group.repo_count = this.repo_relations[group.rg_name].length
//           })
//           this.sortTable('commits_all_time')
//           console.log("LOADED repo groups", this.repo_relations)
//           this.loading = false
//         })
//       })
//     },
//     onCompare (e) {
//       var element = document.getElementById("invalid")
//       this.compCount++
//       let repo = window.AugurAPI.Repo({
//         gitURL: e.target.value
//       })
//       this.$store.commit('addComparedRepo', {
//         gitURL: e.target.value
//       })
//     }, 
//     btoa(s) {
//       return window.btoa(s)
//     }
//   },
//   created() {
//     this.getRepoGroups()
//   },
// }
// /scripdft>
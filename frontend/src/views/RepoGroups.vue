<template>
  <div class="main-content-container container-fluid px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <span class="text-uppercase page-subtitle">Viewing all</span>
        <h3 class="page-title">Repo Groups</h3>
      </div>
    </div>

    <!-- Default Light Table -->
    <div :v-show="loaded" class="row">
      <div class="col">
        <div class="card card-small mb-4">
          <div class="card-header border-bottom">
            <h6 class="m-0">Currently Stored Groups</h6>
          </div>
          <div class="card-body p-0 pb-3 text-center">
            <table style="table-layout:fixed;" class="table mb-0">
              <thead class="bg-light">
                <tr>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_name')"> 
                    <div class="row">
                      <div class="col col-9">Name</div>
                      <div class="col col-3 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'url' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_description')"> 
                    <div class="row">
                      <div class="col col-9">Description</div>
                      <div class="col col-3 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'url' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_website')"> 
                    <div class="row">
                      <div class="col col-9">Website</div>
                      <div class="col col-3 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'url' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_last_modified')"> 
                    <div class="row">
                      <div class="col col-9">Last Modified</div>
                      <div class="col col-3 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'url' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_type')"> 
                    <div class="row">
                      <div class="col col-9">Type</div>
                      <div class="col col-3 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'url' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('repo_count')"> 
                    <div class="row">
                      <div class="col col-9">Repo Count</div>
                      <div class="col col-3 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'url' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0">Options</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="group in repo_groups">
                  <td>
                    <a href="#" @click="onGitRepo(repo)">{{ group.rg_name }}</a>
                  </td>
                  <td>{{ group.rg_description }}</td>
                  <td>{{ group.rg_website }}</td>
                  <td>{{ group.rg_last_modified }}</td>
                  <td>{{ group.rg_type }}</td>
                  <td>{{ group.repo_count }}</td>
                  <td>
                    <div class="row">
                      <d-link id="favorite" class="nav-link col col-2" style="margin-left: 2rem; margin-right: 1rem; padding: 0">
                        <i class="material-icons">star_rate</i>
                        <div class="item-icon-wrapper" />
                      </d-link>
                      <d-tooltip target="#favorite"
                        container=".shards-demo--example--tooltip-01">
                        Consider this repo group as a "favorite" and our workers will regulaly update its metrics' data before others
                      </d-tooltip>
                      <d-link id="add_compare" class="nav-link col col-2" style="padding: 0">
                        <i class="material-icons">library_add</i>
                        <div class="item-icon-wrapper" />
                      </d-link>
                      <d-tooltip target="#add_compare"
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
  import  { Component, Vue } from 'vue-property-decorator';
  import {mapActions, mapGetters} from "vuex";
  @Component({
    methods: {
      ...mapActions('common',[
        'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                    // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
        'getRepoRelations',
      ])
    },
    computed: {
      ...mapGetters('common',[
        'repoRelationsInfo',
        'groupsInfo'
      ])
    },
  })

  export default class RepoGroups extends Vue{
    colors: string[] = ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"];
    testEndpoints: string[] = ['issuesClosed', 'codeChangesLines', 'issueNew'];
    testTimeframes: string[] = ['past 1 month', 'past 3 months', 'past 2 weeks'];
    repos: any[] = [];
    repo_groups:any[] = [];
    repo_relations:any[] =  [];
    themes: string[] = ['dark', 'info', 'royal-blue', 'warning'];
    loadedGroups: boolean = false;
    loadedSparks: boolean = false;
    ascending:boolean = false;
    sortColumn: string ='';

    created() {
      let repo_group_info = this.$store.getters['common/groupsInfo']
      Object.keys(repo_group_info).forEach((key:any) =>{
        this.repo_groups.push(repo_group_info[key])
      })
    }

    sortTable(col: string) {
      if (this.sortColumn === col) {
        this.ascending = !this.ascending;
      } else {
        this.ascending = true;
        this.sortColumn = col;
      }

      var ascending = this.ascending;

      this.repos.sort(function(a, b) {
        if (a[col] > b[col]) {
          return ascending ? 1 : -1
        } else if (a[col] < b[col]) {
          return ascending ? -1 : 1
        }
        return 0;
      })
    }
  }

// export default {
//   components: {
//
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
//     }
//   },
//   methods: {
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
//           console.log("LOADED repo groups", this.repo_relations)
//         })
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
</script>
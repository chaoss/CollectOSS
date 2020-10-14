<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div class="main-content-container container-fluid px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <span class="text-uppercase page-subtitle">Viewing repos within group</span>
        <h3 class="page-title">Repos</h3>
      </div>
    </div>



    <div class="row">
      <div class="col">
        <div class="card card-small mb-4">
          <div class="card-header border-bottom">
            <h6 class="m-0">Currently Stored Repos</h6>
          </div>
          <d-card-body v-if="!loadedRepos"><spinner></spinner></d-card-body>
          <div v-if="loadedRepos" class="card-body p-0 pb-3 text-center">
            <table class="reposInGroupTable table mb-0">
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
                  <!-- <th width="30%" scope="col" class="border-0" v-on:click="sortTable('description')">
                    <div class="row">
                      <div class="col col-9">Repo Description</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'description' == sortColumn"></div>
                    </div>
                  </th> -->
                  <!-- <th scope="col" class="border-0" v-on:click="sortTable('repo_count')">
                    <div class="row">
                      <div class="col col-9">Group's Repo Count</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'repo_count' == sortColumn"></div>
                    </div>
                  </th> -->
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
                  <!-- <th scope="col" class="border-0">Options</th> -->
                </tr>
              </thead>
              <tbody>
                <tr v-for="(repo,index) in sortedReposInGroup(base,sortColumn,ascending)" v-bind:item="repo">
                  <td>
                    <a href="#" @click="onGitRepo(repo)">{{ repo.url }}</a>
                  </td>
                  <td>{{ repo.rg_name }}</td>
                  <!-- <td>{{ repo.description }}</td> -->
                  <!-- <td>{{ repo.repo_count }}</td> -->
                  <td>{{ repo.commits_all_time }}</td>
                  <td>{{ repo.issues_all_time }}</td>
                  <!-- <td>{{ repo.repo_status }}</td> -->
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
                  </td> -->
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

    ...mapActions('compare',[
      'addComparedRepo',
      'setBaseRepo'
    ])
  },
  computed: {
    ...mapGetters('common', [
      'sortedReposInGroup'
    ]),
    ...mapGetters('compare', [
      'base'
    ]),
  },
})

export default class ReposInGroup extends Vue{
  colors: string[] = ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"];
  testEndpoints: string[] = ['issuesClosed', 'codeChangesLines', 'issueNew'];
  testTimeframes: string[] = ['past 1 month', 'past 3 months', 'past 2 weeks'];
  // repos: any[] = [];
  repo_groups:any[] = [];
  repo_relations:any[] =  [];
  themes: string[] = ['dark', 'info', 'royal-blue', 'warning'];
  loadedGroups: boolean = false;
  loadedSparks: boolean = false;

  loadedRepos: boolean = false;

  ascending:boolean = false;
  sortColumn: string ='commits_all_time';
  getRepoRelations!: any
  sortedRepos!:any
  loadRepos!:any;

  addRepo!:any;
  setBaseRepo!:any;
  addComparedRepo!:any;


  created() {

    this.loadRepos().then(() => {
      this.loadedRepos = true
    })

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
    console.log(e)
    this.$router.push({
      name: 'repo_overview',
      params: {group:e.rg_name, repo:e.repo_name, repo_group_id: e.repo_group_id, repo_id: e.repo_id, url:e.url}
    })
  }
}

</script>

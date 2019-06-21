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
    <div :v-show="loaded" class="row">
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
                      <div class="col col-3 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'url' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_name')"> 
                    <div class="row">
                      <div class="col col-9">Repo Group Name</div>
                      <div class="col col-3 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'rg_name' == sortColumn"></div>
                    </div>
                  </th>
                  <th width="30%" scope="col" class="border-0" v-on:click="sortTable('description')">
                    <div class="row">
                      <div class="col col-9">Repo Description</div>
                      <div class="col col-2 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'description' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('repo_count')">
                    <div class="row">
                      <div class="col col-9">Group's Repo Count</div>
                      <div class="col col-2 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'repo_count' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('commits_all_time')">
                    <div class="row">
                      <div class="col col-9">Total Commit Count</div>
                      <div class="col col-2 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'commits_all_time' == sortColumn"></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('issues_all_time')">
                    <div class="row">
                      <div class="col col-0">Total Issue Count</div>
                      <div class="col col-2 arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'issues_all_time' == sortColumn"></div>
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
                <tr v-for="repo in repos">
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
                      <d-link id="favorite_repo" class="nav-link col col-2" style="margin-left: 2rem; margin-right: 1rem; padding: 0">
                        <i class="material-icons">star_rate</i>
                        <div class="item-icon-wrapper" />
                      </d-link>
                      <d-tooltip target="#favorite_repo"
                        container=".shards-demo--example--tooltip-01">
                        Consider this repo group as a "favorite" and our workers will regulaly update its metrics' data before others
                      </d-tooltip>
                      <d-link id="add_compare_repo" class="nav-link col col-2" style="padding: 0">
                        <i class="material-icons">library_add</i>
                        <div class="item-icon-wrapper" />
                      </d-link>
                      <d-tooltip target="#add_compare_repo"
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
<script>

export default {
  components: {

  },
  computed: {
  },
  data() {
    return {
      colors: ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      testEndpoints: ['codeCommits', 'closedIssues', 'openIssues'],
      testTimeframes: ['past 1 month', 'past 3 months', 'past 2 weeks'],
      repos: [],
      repo_groups: [],
      repo_relations: {},
      themes: ['dark', 'info', 'royal-blue', 'warning'],
      loaded: false,
      ascending: false,
      sortColumn: '',
      group_id_name_map: {},
    }
  },
  methods: {
    sortTable(col) {
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
    },
    getRepoGroups() {
      console.log("START")
      window.AugurAPI.getRepos().then((data) => {
        this.repos = data
        console.log("LOADED repos", this.repos)
        window.AugurAPI.getRepoGroups().then((data) => {
          $(this.$el).find('.spinner').removeClass('loader')
          $(this.$el).find('.spinner').removeClass('relative')
          this.repo_groups = data
          //move down between future relation endpoint
          this.repo_groups.forEach((group) => {
            this.repo_relations[group.rg_name] = this.repos.filter(function(repo){
              return repo.rg_name == group.rg_name
            })
            group.repo_count = this.repo_relations[group.rg_name].length
          })
          this.sortTable('commits_all_time')
          console.log("LOADED repo groups", this.repo_relations)
          this.loading = false
        })
      })
    },
    onCompare (e) {
      var element = document.getElementById("invalid")
      this.compCount++
      let repo = window.AugurAPI.Repo({
        gitURL: e.target.value
      })
      this.$store.commit('addComparedRepo', {
        gitURL: e.target.value
      })
    }, 
    btoa(s) {
      return window.btoa(s)
    }
  },
  created() {
    this.getRepoGroups()
  },
}
</script>
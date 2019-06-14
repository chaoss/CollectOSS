<template>
  <div class="main-content-container container-fluid px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <span class="text-uppercase page-subtitle">Viewing all</span>
        <h3 class="page-title">Repos</h3>
      </div>
    </div>

    <bar-loader class="" color="#bada55" :loading="loading" :size="150"></bar-loader>
    <!-- Default Light Table -->
    <div :v-show="!loading" class="row">
      <div class="col">
        <div class="card card-small mb-4">
          <div class="card-header border-bottom">
            <h6 class="m-0">Currently Stored Repos</h6>
          </div>
          <div class="card-body p-0 pb-3 text-center">
            <table class="table mb-0">
              <thead class="bg-light">
                <tr>
                  <th scope="col" class="border-0">Repo ID</th>
                  <th scope="col" class="border-0">Group Name</th>
                  <th scope="col" class="border-0">Repo Name</th>
                  <th scope="col" class="border-0">Git URL</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="repo in repos">
                  <td>{{ repo.repo_id }}</td>
                  <td>{{ repo.rg_name }}</td>
                  <td>{{ repo.repo_name }}</td>
                  <td>{{ repo.url }}</td>
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
      loading: true
    }
  },
  methods: {
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
          console.log("LOADED repo groups", this.repo_relations)
          this.loading = false
        })
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
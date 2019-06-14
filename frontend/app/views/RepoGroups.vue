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
    <div class="row">
      <div class="col">
        <div class="card card-small mb-4">
          <div class="card-header border-bottom">
            <h6 class="m-0">Currently Stored Groups</h6>
          </div>
          <div class="card-body p-0 pb-3 text-center">
            <table class="table mb-0">
              <thead class="bg-light">
                <tr>
                  <th scope="col" class="border-0">Repo Group ID</th>
                  <th scope="col" class="border-0">Name</th>
                  <th scope="col" class="border-0">Description</th>
                  <th scope="col" class="border-0">Website</th>
                  <th scope="col" class="border-0">Last Modified</th>
                  <th scope="col" class="border-0">Type</th>
                  <th scope="col" class="border-0">Repo Count</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="group in repo_groups">
                  <td>{{ group.repo_group_id }}</td>
                  <td>{{ group.rg_name }}</td>
                  <td>{{ group.rg_description }}</td>
                  <td>{{ group.rg_website }}</td>
                  <td>{{ group.rg_last_modified }}</td>
                  <td>{{ group.rg_type }}</td>
                  <td>{{ group.repo_count }}</td>
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
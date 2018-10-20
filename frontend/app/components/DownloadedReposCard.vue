<template>
  <div class="row section collapsible collapsed">
    <hr>
    <div v-for="project in projects" class="col-6">
      <h4>{{ project }}</h4>
      <div class="repo-link-holder">
        <table class="is-responsive">
          <thead class="repo-link-table repo-link-table-body">
            <tr>
              <th>URL</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody class="repo-link-table repo-link-table-body">
            <tr v-for="repo in repos[project]">
              <td><a :href="'?git=' + btoa(repo.url)" class="repolink fade">{{ repo.url }}</a></td>
              <td>{{ repo.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>

module.exports = {
  data () { return {
    repos: {},
    projects: []
  }},
  methods: {
    onRepo (e) {
      this.$store.commit('setRepo', {
        githubURL: e.target.value
      })
    },
    getDownloadedRepos() {
      this.downloadedRepos = []
      window.AugurAPI.getDownloadedGitRepos().then((data) => {
        this.repos = window._.groupBy(data, 'project_name')
        this.projects = Object.keys(this.repos)
      })
    },
    btoa(s) {
      return window.btoa(s)
    }
  },
  mounted() {
    this.getDownloadedRepos()
  } 
};

</script>
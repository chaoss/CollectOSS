<template>
  <!-- <div class="row section collapsible collapsed"> -->
<section class="unmaterialized">
  <h3>Downloaded Git Repos by Project</h3>
  <div class="row section">
    <hr>
    <div style=" margin-left: 42.4%" class="col col-12 relative spinner loader"></div>
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
                <td><!-- <router-link :to="'git/' + (repo.url).slice(11)" @click.prevent="onGitRepo(repo)" class="repolink fade">{{ repo.url }}</router-link> --><!-- <a :href="'?git=' + btoa(repo.url)" class="repolink fade">{{ repo.url }}</a> -->
                  <a href="#" @click="onGitRepo(repo)">{{ repo.url }}</a>
                </td>
                <td>{{ repo.status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </section>
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
    onGitRepo (e) {
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
      this.$store.commit('setRepo', {
        gitURL: e.url
      })

      this.$store.commit('setTab', {
        tab: 'git'
      })

      this.$router.push({
        name: 'git',
        params: {repo: e.url}
      })
    },
    getDownloadedRepos() {
      this.downloadedRepos = []
      window.AugurAPI.getDownloadedGitRepos().then((data) => {
        $(this.$el).find('.spinner').removeClass('loader')
        $(this.$el).find('.spinner').removeClass('relative')
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
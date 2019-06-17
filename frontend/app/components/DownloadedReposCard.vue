<template>
  <!-- <div class="row section collapsible collapsed"> -->
<section class="unmaterialized">
  <h3>Downloaded Git Repos by Project</h3>
  <div class="row section">
    <hr>
    <div style=" margin-left: 42.4%" class="col col-12 relative spinner loader"></div>
    <!-- <div v-for="project in projects" class="col-6"> -->
    <div v-if="loaded" class="col-12">
      <h4>{{ project }}</h4>
        <div class="repo-link-holder">
          <table class="is-responsive">
            <thead class="repo-link-table repo-link-table-body">
              <tr>
                <th v-on:click="sortTable('url')">  URL <div class="arrow" v-if="'url' == sortColumn" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div></th>
                <th v-on:click="sortTable('rg_name')">  Repo Group Name <div class="arrow" v-if="'rg_name' == sortColumn" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div></th>
                <th v-on:click="sortTable('rg_description')">  Repo Group Description <div class="arrow" v-if="'rg_description' == sortColumn" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div></th>
                <th v-on:click="sortTable('repo_status')">  Status <div class="arrow" v-if="'repo_status' == sortColumn" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div></th>
              </tr>
            </thead>
            <tbody class="repo-link-table repo-link-table-body">
              <tr v-for="repo in repos">
                <td>
                  <a href="#" @click="onGitRepo(repo)">{{ repo.url }}</a>
                </td>
                <td>{{ repo.rg_name }}</td>
                <td>{{ repo.rg_description }}</td>
                <td>{{ repo.repo_status }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      <!-- </div> -->
      </div>
    </div>
  </section>
</template>

<script>
module.exports = {

  components: {

  },
  data () { return {
    repos: {},
    repo_groups: [],
    repo_relations: {},
    loaded: false,
    ascending: false,
    sortColumn: '',
  }},
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
          this.loaded = true
        })
      })
    },
    btoa(s) {
      return window.btoa(s)
    }
  },
  mounted() {
    this.getRepoGroups()
  } 
};

</script>
<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div class="main-content-container container-fluid px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <span class="text-uppercase page-subtitle">Overview</span>
        <h3 class="page-title">Projects</h3>
      </div>
    </div>

    <!-- Default Light Table -->
    <div class="row">
      <div class="col">
        <div class="card card-small mb-4">
          <div class="card-header border-bottom">
            <h6 class="m-0">Active Users</h6>
          </div>
          <div class="card-body p-0 pb-3 text-center">
            <table class="table mb-0">
              <thead class="bg-light">
                <tr>
                  <th scope="col" class="border-0">#</th>
                  <th scope="col" class="border-0">First Name</th>
                  <th scope="col" class="border-0">Last Name</th>
                  <th scope="col" class="border-0">Country</th>
                  <th scope="col" class="border-0">City</th>
                  <th scope="col" class="border-0">Phone</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>1</td>
                  <td>Ali</td>
                  <td>Kerry</td>
                  <td>Russian Federation</td>
                  <td>Gdańsk</td>
                  <td>107-0339</td>
                </tr>
                <tr>
                  <td>2</td>
                  <td>Clark</td>
                  <td>Angela</td>
                  <td>Estonia</td>
                  <td>Borghetto di Vara</td>
                  <td>1-660-850-1647</td>
                </tr>
                <tr>
                  <td>3</td>
                  <td>Jerry</td>
                  <td>Nathan</td>
                  <td>Cyprus</td>
                  <td>Braunau am Inn</td>
                  <td>214-4225</td>
                </tr>
                <tr>
                  <td>4</td>
                  <td>Colt</td>
                  <td>Angela</td>
                  <td>Liberia</td>
                  <td>Bad Hersfeld</td>
                  <td>1-848-473-7416</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>

    <!-- Default Dark Table -->
    <div class="row">
      <div class="col">
        <div class="card card-small overflow-hidden mb-4">
          <div class="card-header bg-dark">
            <h6 class="m-0 text-white">Inactive Users</h6>
          </div>
          <div class="card-body p-0 pb-3 bg-dark text-center">
            <table class="table table-dark mb-0">
              <thead class="thead-dark">
                <tr>
                  <th scope="col" class="border-bottom-0">#</th>
                  <th scope="col" class="border-bottom-0">First Name</th>
                  <th scope="col" class="border-bottom-0">Last Name</th>
                  <th scope="col" class="border-bottom-0">Country</th>
                  <th scope="col" class="border-bottom-0">City</th>
                  <th scope="col" class="border-bottom-0">Phone</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>1</td>
                  <td>Graham</td>
                  <td>Brent</td>
                  <td>Benin</td>
                  <td>Ripabottoni</td>
                  <td>1-512-760-9094</td>
                </tr>
                <tr>
                  <td>2</td>
                  <td>Clark</td>
                  <td>Angela</td>
                  <td>Estonia</td>
                  <td>Borghetto di Vara</td>
                  <td>1-660-850-1647</td>
                </tr>
                <tr>
                  <td>3</td>
                  <td>Wylie</td>
                  <td>Joseph</td>
                  <td>Korea, North</td>
                  <td>Guelph</td>
                  <td>325-4351</td>
                </tr>
                <tr>
                  <td>4</td>
                  <td>Garth</td>
                  <td>Clementine</td>
                  <td>Indonesia</td>
                  <td>Narcao</td>
                  <td>722-8264</td>
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
      repos: {},
      repo_groups: [],
      themes: ['dark', 'info', 'royal-blue', 'warning']
    }
  },
  methods: {
    getDownloadedRepos() {
      console.log("START")
      let AugurAPI = new AugurAPI()
      AugurAPI.getRepos().then((data) => {
        this.repos = data
      })

      AugurAPI.getRepoGroups().then((data) => {
        $(this.$el).find('.spinner').removeClass('loader')
        $(this.$el).find('.spinner').removeClass('relative')
        this.repo_groups = data
        this.loaded = true
      })
    },
    btoa(s) {
      return window.btoa(s)
    }
  },
  created() {
    this.getDownloadedRepos()
  },
}
</script>
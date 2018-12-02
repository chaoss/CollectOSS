<template>
  <header class="hide-print">
    <div class="content">
      <div class="row auto">
        <div class="col col-3">
          <a href="/">
            <img src="/static/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/>
          </a>
        </div>
        <div class="col col-5">
          <div class="form-item">
            <input type="text" class="search reposearch" name="headersearch" placeholder="GitHub URL" @change="onRepo">
          </div>
        </div>
        <nav class="col col-4 header-nav">
          <a class="header-nav-item" href="https://github.com/chaoss/augur">GitHub</a>
          <a class="header-nav-item" href="static/docs/">Python Docs</a>
          <a class="header-nav-item" href="static/api_docs/">API Docs</a>
          <router-link class="header-nav-item" to="/metrics_status">Metrics Status</router-link>
        </nav>
      </div>
    </div>
  </header>
</template>


<script>

module.exports = {
  methods: {
    onRepo (e) {
      this.$store.commit('setRepo', {
        githubURL: e.target.value
      })
      let link = '/gmd/' + (e.target.value)
      this.$router.push({
        path: link
        // path: "/git"
      })
    }
  } 
};

</script>
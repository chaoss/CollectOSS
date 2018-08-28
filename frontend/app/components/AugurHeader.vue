<template>
  <header class="hide-print">
    <div class="content">
      <div class="row auto">
        <div class="col col-3">
          <a href="/">
            <img src="static/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/>
          </a>
        </div>
        <div class="col col-5">
          <div class="form-item">
            <input type="text" class="search reposearch" name="headersearch" placeholder="GitHub URL" @change="onRepo">
          </div>
        </div>
        <nav class="col col-4 header-nav">
          <a class="header-nav-item" href="https://github.com/OSSHealth/augur">GitHub</a>
          <a class="header-nav-item" href="static/docs">Python Docs</a>
          <a class="header-nav-item" href="static/api_docs">API Docs</a>
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
    }
  } 
};

</script>
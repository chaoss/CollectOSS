<template>
  <header class="hide-print">
    <div class="content">
      <div class="row">
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
        <div class="col col-5">
          <div class="form-item">
            <input type="text" class="search reposearch" name="headersearch" placeholder="Compared GitHub URL" @change="onCompare">
          </div>
        </div>
        <div class="col col-4 push-right">

        </div>
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
    },
    onCompare (e) {
      this.$store.commit('addComparedRepo', {
        githubURL: e.target.value
      })
    },
  }
};

</script>

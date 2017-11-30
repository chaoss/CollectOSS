<template>
  <header class="hide-print">
    <div class="content">
      <div class="row">
        <div class="col col-4">
          <img src="img/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/>
        </div>
        <div class="col col-5 push-right">
          <div class="form-item">
              <input type="text" class="search reposearch" name="headersearch" placeholder="GitHub URL" @change="onRepo">
          </div>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
module.exports = {
  methods: {
    onRepo (e) {
      this.$store.commit('setBaseRepo', {
        url: e.target.value
      })
    }
  } 
}
</script>
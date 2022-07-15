<!-- #SPDX-License-Identifier: MIT -->
<template>
  <header class="hide-print">
    <div class="content">
      <div class="row auto">
        <div class="col col-3">
          <a href="/">
            <img src="@/assets/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/>
          </a>
        </div>
        <div class="col col-4">
          <div class="form-item">
            <input type="text" class="search reposearch" name="headersearch" placeholder="GitHub URL" @change="onRepo">
          </div>
        </div>
        <nav class="col col-5 header-nav">
          <a class="header-nav-item loginlink" :href="logoutLink" v-if="user">Logout</a>
          <router-link class="header-nav-item loginlink" to="/login" v-if="!user">Login</router-link>
          <router-link class="header-nav-item loginlink" to="/profile" v-if="user">{{ user }}</router-link>
          <a class="header-nav-item" href="https://github.com/chaoss/augur">GitHub</a>
          <a class="header-nav-item" href="/static/docs/">Python</a>
          <a class="header-nav-item" href="/static/api_docs/">API</a>
          <router-link class="header-nav-item" to="/metrics_status">Metrics</router-link>
        </nav>
      </div>
    </div>
  </header>
</template>

<script>
export default{
  data () {
    return {
      'user': AUGUR_SESSION['username'],
      'logoutLink': '/logout?next=' + encodeURI('http://' + window.location.host)
    }
  },
   methods: {
    onRepo (e) {
      let repo = window.AugurAPI.Repo({
          githubURL: e.target.value
        })
      if(!repo.batch(['codeCommits'], true)[0]){
        alert("The repo " + repo.githubURL + " could not be found. Please try again.")
      } else {
        this.$store.commit('resetBaseRepo')
        this.$store.commit('setRepo', {
          githubURL: e.target.value
        })
        this.$router.push({
          name: 'gmd',
          params: {owner: repo.owner, repo: repo.name, repoID: repo.repoID, repoGroupID: repo.repoGroupID}
        })
        window.location.reload()
      }
      
    }
  }
};

</script>

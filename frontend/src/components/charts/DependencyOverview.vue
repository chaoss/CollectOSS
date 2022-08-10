<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div>
    <div class="row">
      <div class="col col-6">
        <h3>Top Dependents</h3>
        <div class="deps" ref="dependents">
          <span>Loading...</span>
        </div>
      </div>
      <div class="col col-6">
        <h3>Top Dependencies</h3>
        <div class="deps" ref="dependencies">
          <span>Loading...</span>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
  export default {
    props: [],
    computed: {
      repo() {
        return this.$store.state.baseRepo
      },
      dependencies() {
        if (this.repo) {

          this.$refs['dependents'].innerHTML = 'Loading...';
          window.AugurRepos[this.repo].dependents().then((dependents) => {
            if (!dependents || !dependents.length) {
              this.$refs['dependents'].innerHTML = 'No dependents found.'
            }
            this.$refs['dependents'].innerHTML = '';
            for (let i = 0; i < dependents.length && i < 10; i++) {
              this.$refs['dependents'].innerHTML += dependents[i].name + '<br>'
            }
          }, () => {
            this.$refs['dependents'].innerHTML = 'No data.'
          });

          this.$refs['dependencies'].innerHTML = '';
          window.AugurRepos[this.repo].dependencies().then((dependencies) => {
            if (!dependencies || !dependencies.length) {
              this.$refs['dependencies'].innerHTML = 'No dependencies found.'
            }
            this.$refs['dependencies'].innerHTML = '';
            for (let i = 0; i < dependencies.dependencies.length && i < 10; i++) {
              this.$refs['dependencies'].innerHTML += dependencies.dependencies[i].name + '<br>'
            }
          }, () => {
            this.$refs['dependencies'].innerHTML = 'No data.'
          })

        }
      }
    }
  };
</script>

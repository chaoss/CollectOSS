<template>
  <div>
    <div class="row">
      <div class="col col-6">
        <h3>Total Dependents</h3>
        <div class="deps" ref="totaldependents">
          Loading...
        </div>
      </div>
      <div class="col col-6">
        <h3>Total Dependencies</h3>
        <div class="deps" ref="totaldependencies">
          Loading...
        </div>
      </div>
    </div>
    <div class="row">
      <div class="col col-6">
        <h3>Top Dependents</h3>
        <div class="deps" ref="dependents">
          Loading...
        </div>
      </div>
      <div class="col col-6">
        <h3>Top Dependencies</h3>
        <div class="deps" ref="dependencies" v-html="dependencies">
          Loading...
        </div>
      </div>
    </div> 
  </div> 
</template>


<script>

  import GHDataStats from '../../GHDataStats'
  import * as d3 from 'd3'

  export default {
    props: [],
    computed: {
      repo() {
        return this.$store.state.baseRepo
      },
      dependencies() {
        if (this.repo) {
          window.GHDataRepos[this.repo].dependents().then((dependents) => {
            this.$refs['dependents'].innerHTML = ''
            for (var i = 0; i < dependents.length && i < 10; i++) {
              this.$refs['dependents'].innerHTML += dependents[i].name + '<br>'
            }
          })
          window.GHDataRepos[this.repo].dependencies().then((dependencies) => {
            this.$refs['dependencies'].innerHTML = ''
            for (var i = 0; i < dependencies.dependencies.length && i < 10; i++) {
              this.$refs['dependents'].innerHTML += dependencies.dependencies[i].name + '<br>'
            }
          })
          window.GHDataRepos[this.repo].dependencyStats().then((depstats) => {
            this.$refs['totaldependents'].innerHTML   = depstats['dependent_repositories']
            this.$refs['totaldependencies'].innerHTML = depstats['dependencies']
          })
        }
      }
    }
  };

</script>
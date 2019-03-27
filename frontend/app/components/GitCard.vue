<template>
  <section>
    <div style="display: inline-block;">
      <h2 style="display: inline-block; color: black !important">{{ $store.state.gitRepo }}</h2>
      <h2 style="display: inline-block;" class="repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 style="display: inline-block;" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span> 
      </h2>
    </div>
        <div v-if="!loaded" style="text-align: center; margin-left: 44.4%; position: relative !important" class="col col-12 spinner loader"></div>

      
      <div class="row" style="transform: translateY(-40px) !important" v-if="loaded">
        <div class="col col-12">
          <tick-chart source="changesByAuthor" :data="values['changesByAuthor']"></tick-chart>
        </div>
        
        <div class="col col-6" style="padding-right: 35px; transform: translateY(-70px) !important">
          <normalized-stacked-bar-chart title="Lines of code added by the top 10 authors as Percentages - By Time Period"></normalized-stacked-bar-chart>
        </div>
        <div class="col col-6" style="padding-left: 65px; transform: translateY(-70px) !important">
          <div style="padding-top: 35px"></div>
          <horizontal-bar-chart measure="lines" title="Average Lines of Code Per Commit"></horizontal-bar-chart>
        </div>
      </div>
      <div style="transform: translateY(-180px) !important" class="row" v-if="loaded">
        <div class="col col-6">
          <one-dimensional-stacked-bar-chart type="lines" title="Lines of Code Added by the top 10 Authors as Percentages - All Time"></one-dimensional-stacked-bar-chart>
        </div>
        <div class="col col-6">
          <one-dimensional-stacked-bar-chart type="commit" title="Commits by the top 10 Authors as Percentages - All Time"></one-dimensional-stacked-bar-chart>
        </div>
      </div>

      <div class="row" style="transform: translateY(-190px) !important" v-if="loaded">
        <lines-of-code-chart></lines-of-code-chart>
      </div>
    </div>
  </section>
</template>

<script>

import AugurHeader from './AugurHeader'
import TickChart from './charts/TickChart'
import LinesOfCodeChart from './charts/LinesOfCodeChart'
import NormalizedStackedBarChart from './charts/NormalizedStackedBarChart'
import OneDimensionalStackedBarChart from './charts/OneDimensionalStackedBarChart'
import HorizontalBarChart from './charts/HorizontalBarChart'

module.exports = {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      values: {},
      loaded: false
    }
  },
  components: {
    AugurHeader,
    TickChart,
    LinesOfCodeChart,
    NormalizedStackedBarChart,
    OneDimensionalStackedBarChart,
    HorizontalBarChart
  },
  computed: {
    repo () {
      return this.$store.state.baseRepo
    },
    gitRepo () {
      return this.$store.state.gitRepo
    },
    comparedRepos () {
      return this.$store.state.comparedRepos
    },
    // loaded() {
    //   return this.loaded1 && this.loaded2
    // }
  },
created() {
    let repos = []
    if (this.repo) {
      if (window.AugurRepos[this.repo])
        repos.push(window.AugurRepos[this.repo])
      // repos.push(this.repo)
    } // end if (this.$store.repo)
    this.comparedRepos.forEach(function(repo) {
      repos.push(window.AugurRepos[repo])
    });
    let endpoints1 = [
"changesByAuthor",
    ]

    endpoints1.forEach((source) => {
      let repo = window.AugurAPI.Repo({ gitURL: this.gitRepo })
      repo[source]().then((data) => {
        console.log("batch data", data)
        this.values[source] = data
        this.loaded=true
      }, () => {
            //this.renderError()
      }) // end batch request
    })
  }
}

</script>
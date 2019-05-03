<template>
  <section>
    <div style="display: inline-block;">
      <h2 v-if="loaded" style="display: inline-block; color: black !important">Project Overview: {{ project }}</h2>
      <p></p>
    </div>
      <div class="row" style="transform: translateY(-50px) !important">

        <div class="col col-6" style="padding-right: 35px">
          <grouped-bar-chart source="cdRgTpRankedCommits"
          title="Top Repos in 2018 by Commits with Baseline Averages - Sorted"
          field="commit"></grouped-bar-chart>
        </div>
        <div class="col col-6" style="padding-right: 35px">
          <grouped-bar-chart source="cdRgTpRankedLoc"
          title="Top Repos in 2018 by Net LoC with Baseline Averages - Sorted"
          field="loc"></grouped-bar-chart>
        </div>
        <div class="col col-6" style="padding-right: 35px">
          <grouped-bar-chart source="cdRgNewrepRankedCommits"
          title="Top New Repos in 2018 by Commits with Baseline Averages - Sorted"
          field="commit"></grouped-bar-chart>
        </div>
        <div class="col col-6" style="padding-right: 35px">
          <grouped-bar-chart source="cdRgNewrepRankedLoc"
          title="Top New Repos in 2018 by Net LoC with Baseline Averages - Sorted"
          field="loc"></grouped-bar-chart>

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
import GroupedBarChart from './charts/GroupedBarChart'
import StackedBarChart from './charts/StackedBarChart'
module.exports = {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      loaded: false,
      project: null
    }
  },
  computed: {
    gitRepo () {
      return this.$store.state.gitRepo
    },
  },
  components: {
    AugurHeader,
    TickChart,
    LinesOfCodeChart,
    NormalizedStackedBarChart,
    OneDimensionalStackedBarChart,
    HorizontalBarChart,
    GroupedBarChart,
    StackedBarChart
  },
  mounted() {
    let repo = window.AugurAPI.Repo({ gitURL: this.gitRepo })

    repo.facadeProject().then((data) => {
      this.project = data[0].name
      console.log(this.project, "here")
      this.loaded=true
    })
  }
}
</script>

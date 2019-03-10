<template>
  <section>
    <div style="display: inline-block;">
      <h2 style="display: inline-block; color: black !important">{{ $store.state.gitRepo }}</h2>
      <h2 style="display: inline-block;" class="repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 style="display: inline-block;" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span> 
      </h2>
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
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
    }
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
  }
}
</script>
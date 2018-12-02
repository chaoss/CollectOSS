<template>
  <section>
    <h1>Git Metrics</h1>
    <h2>{{ $store.state.gitRepo }}</h2>
      <tick-chart></tick-chart>
      <div class="row">
        <div class="col col-6">
          <normalized-stacked-bar-chart title="Lines of code added by the top 10 authors as Percentages - By Time Period"></normalized-stacked-bar-chart>
        </div>
        <div class="col col-6" style="padding-left: 10px">
          <div style="padding-top: 75px"></div>
          <one-dimensional-stacked-bar-chart type="commit" title="Commits by the top 10 Authors as Percentages - All Time"></one-dimensional-stacked-bar-chart>
          <div style="padding-top: 15px"></div>
          <one-dimensional-stacked-bar-chart type="lines" title="Lines of Code Added by the top 10 Authors as Percentages - All Time"></one-dimensional-stacked-bar-chart>
        </div>
      </div>
      <!-- <normalized-stacked-bar-chart></normalized-stacked-bar-chart>
      <one-dimensional-stacked-bar-chart type="commit" title="Commits by the top 10 Authors as Percentages - By Time Period"></one-dimensional-stacked-bar-chart>
      <one-dimensional-stacked-bar-chart type="lines" title="Lines of Code Added by the top 10 Authors as Percentages - By Time Period"></one-dimensional-stacked-bar-chart> -->
      <div class="row">
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

module.exports = {
  components: {
    AugurHeader,
    TickChart,
    LinesOfCodeChart,
    NormalizedStackedBarChart,
    OneDimensionalStackedBarChart
  }
}

</script>

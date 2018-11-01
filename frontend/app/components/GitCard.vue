<template>
  <section>
    <h1>Git Metrics</h1>
    <h2>{{ $store.state.gitRepo }}</h2>
      <h3>Top ten authors</h3>
      <tick-chart></tick-chart>
      <div class="row">
        <lines-of-code-chart></lines-of-code-chart>
      </div>
    </div>
  </section>
</template>

<script>

import TickChart from './charts/TickChart'
import LinesOfCodeChart from './charts/LinesOfCodeChart'

module.exports = {
  components: {
    TickChart,
    LinesOfCodeChart
  }
}

</script>

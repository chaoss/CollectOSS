<template>
  <section>
    <h1>Git Metrics</h1>
    <h2>{{ $store.state.gitRepo }}</h2>
      <div class="row">
        <lines-of-code-chart></lines-of-code-chart>
      </div>
    </div>
  </section>
</template>

<script>

import LineChart from './charts/LineChart'
import LinesOfCodeChart from './charts/LinesOfCodeChart'

module.exports = {
  components: {
    LineChart,
    LinesOfCodeChart
  }
}

</script>

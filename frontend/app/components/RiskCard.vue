<template>
  <section>
    <h1>Risk</h1>
    <h2>{{ $store.state.baseRepo }}   {{ $store.state.comparedRepo }}</h2>
      <div class="row">
        <p>We currently do not have any metrics developed for this group.</p>
      </div>
    </div>

  </section>
</template>

<script>

import LineChart from './charts/LineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'

module.exports = {
  components: {
    LineChart,
    BubbleChart,
    StackedBarChart
  }
}

</script>

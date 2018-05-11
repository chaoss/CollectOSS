<template>
  <section>
    <h1>Risk</h1>
    <h2>{{ $store.state.baseRepo }}</h2>
      <div class="row">
        <p>These metrics have not yet been developed.</p>
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

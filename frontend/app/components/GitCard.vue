<template>
  <section>
    <h1>Git Metrics</h1>
    <h2>{{ $store.state.baseRepo }}</h2>
      <div class="row">
        <facade-chart></facade-chart>
      </div>
    </div>
  </section>
</template>

<script>

import LineChart from './charts/LineChart'
import FacadeChart from './charts/FacadeChart'

module.exports = {
  components: {
    LineChart,
    FacadeChart
  }
}

</script>

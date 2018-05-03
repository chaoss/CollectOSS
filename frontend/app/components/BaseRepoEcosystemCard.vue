<template>
  <section>
    <h1>Ecosystem</h1>
    <h2>{{ $store.state.baseRepo }}</h2>

    <div class="row">
      <div class="col col-6">
        <line-chart source="downloads"
                    title="Downloads / Day" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="stars"
                    title="Stars / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </line-chart>
      </div>
    </div>

    <div class="col col-6">
      <bus-factor source="busFactor"
                  title="Bus Factor"
                  cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics-list.md"
                  cite-text="Pony Factor">
        <!-- cite URL to be updated when changes are pulled for pony factor -->
      </bus-factor>
    </div>

    <div class="row">
      <div class="col col-12">
        <dependency-overview></dependency-overview>
      </div>
    </div>


  </section>
</template>

<script>

import LineChart from './charts/LineChart'
import DependencyOverview from './charts/DependencyOverview'
import BusFactor from './charts/BusFactor'

module.exports = {
  components: {
    LineChart,
    DependencyOverview,
    BusFactor
  }
};

</script>
<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <h1>Ecosystem</h1>
    <div class="baseRepo">
      <h2 class="baseRepoh2">{{ $store.state.baseRepo }}</h2>
      <h2 class="repolisting baseRepo" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 class="baseRepo" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span> 
      </h2>
    </div>

    <div class="row">
      <div class="col col-6">
        <dynamic-line-chart source="downloads"
                    title="Downloads / Day" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="stars"
                    title="Stars / Week" 
                    cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/community-activity.md"
                    cite-text="Community Activty">
        </dynamic-line-chart>
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

import DynamicLineChart from './charts/DynamicLineChart'
import DependencyOverview from './charts/DependencyOverview'
import BusFactor from './charts/BusFactor'

export default {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
    }
  },
  components: {
    DynamicLineChart,
    DependencyOverview,
    BusFactor
  }
};

</script>
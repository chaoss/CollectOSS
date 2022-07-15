<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <h1>Value</h1>
    <div class="valueCard">
      <h2 class="valueC">{{ $store.state.baseRepo }}</h2>
      <h2 class="valueCard repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 class="valueCard" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span> 
      </h2>
    </div>
      <div class="row">
        <p>We currently do not have any metrics developed for this group.</p>
      </div>
    </div>

  </section>
</template>

<script>

import DynamicLineChart from './charts/DynamicLineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'

export default {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
    }
  },
  components: {
    DynamicLineChart,
    BubbleChart,
    StackedBarChart
  }
}

</script>

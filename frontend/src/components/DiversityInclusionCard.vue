<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <div class="baseRepo">
      <h2 class="baseRepoh2">{{ $store.state.baseRepo }}</h2>
      <h2
        class="baseRepo repolisting"
        v-if="$store.state.comparedRepos.length > 0"
      >
        compared to:
      </h2>
      <h2
        class="baseRepo"
        v-for="(repo, index) in $store.state.comparedRepos"
        :key="index"
      >
        <span v-bind:style="{ color: colors[index] }" class="repolisting">
          {{ repo }}
        </span>
      </h2>
    </div>
    <div class="row">
      <p>We currently do not have any metrics developed for this group.</p>
    </div>
  </section>
</template>

<script>
import DynamicLineChart from "./charts/DynamicLineChart.vue";
import BubbleChart from "./charts/BubbleChart.vue";
import StackedBarChart from "./charts/StackedBarChart.vue";

export default {
  data() {
    return {
      colors: [
        "#FF3647",
        "#4736FF",
        "#3cb44b",
        "#ffe119",
        "#f58231",
        "#911eb4",
        "#42d4f4",
        "#f032e6",
      ],
    };
  },
  components: {
    DynamicLineChart,
    BubbleChart,
    StackedBarChart,
  },
};
</script>

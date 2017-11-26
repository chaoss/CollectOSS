<template>
  <div ref="chart" class="linechart"></div>
</template>


<script>

  import MG from 'metrics-graphics'
  import GHDataStats from '../GHDataStats'
  import * as d3 from 'd3'

  MG.data_graphic({
    title: "Missing Data",
    error: 'Data unavaliable for ' + title,
    chart_type: 'missing-data',
    missing_text: title + ' could not be loaded',
    target: this.$refs.chart,
    full_width: true,
    height: 200
  });

</script>
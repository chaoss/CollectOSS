<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div ref="chart" class="linechart"></div>
</template>


<script>
  export default {
    computed: {
      chart() {
        MG.data_graphic({
          title: "Missing Data",
          error: 'Data unavaliable',
          chart_type: 'missing-data',
          missing_text: 'Data could not be loaded',
          target: this.$refs.chart,
          full_width: true,
          height: 200
        });
      }
    }
  }
</script>

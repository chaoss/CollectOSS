<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div ref="holder" class="insightChartDiv">
    <spinner v-if="!loaded" class="insightChartSpinner"></spinner>
    <vega-lite v-if="loaded" :spec="spec(vegaSpec)" :data="values" center="true" id="vegaChart"></vega-lite>
  </div>
</template>

<script>
  import Spinner from "../Spinner.vue";
  import vegaEmbed from "vega-embed";

  export default {
    props: ["url", "source", "title", "color", "data"],
    components: {
      Spinner
    },
    data() {
      return {
        values: [],
        user: null,
        loaded: false,
        x: 0,
        y: 0,
        vegaSpec: null
      };
    },
    mounted() {
      this.calculateVegaSpec();
      this.$nextTick(() => {
        window.onresize = this.calculateVegaSpec;
        console.log(window);
      });
    },
    computed: {
      earliest() {
        if (!this.values[0]) return null;
        let date = new Date(this.values[0].date);
        date.setYear(2020);
        return date
      },
      latest() {
        return this.values[0] ? new Date(this.values[this.values.length - 1].date) : null;
      }
    },
    methods: {
      spec(vegaSpec) {
        vegaEmbed('#vegaChart', vegaSpec, {
          mode: 'vega-lite'
        });
        return vegaSpec;
      },
      calculateVegaSpec() {
        this.loaded = false;
        let specWidth = this.$refs.holder.clientWidth * 0.75;
        let specHeight = this.$refs.holder.clientHeight * 0.75;
        this.values = this.data;
        this.includeNullDates();
        this.vegaSpec = {
          $schema: "https://vega.github.io/schema/vega-lite/v2.json",
          center: true,
          width: specWidth, //263.7,
          height: specHeight, //166,
          padding: {left: specWidth * .1, top: 10, right: 0, bottom: 5},
          layer: [
            {
              mark: {
                type: "line",
                interpolate: "basis"
              },
              encoding: {
                x: {
                  field: "date",
                  type: "temporal",
                  axis: {grid: false, format: "%b %d"},
                  domain: [this.earliest, this.latest]
                },
                y: {
                  field: "value",
                  type: "quantitative",
                  axis: {grid: false, title: false, ticks: false}
                },
                color: {value: this.color}
              }
            },
          ]
        };
        this.loaded = true;
        vegaEmbed('#vegaChart', this.vegaSpec, {
          mode: 'vega-lite'
        });
      },
      renderChart() {
      },
      convertKey(ary) {
        ary.forEach(el => {
          let keys = Object.keys(el);
          let field = null;
          keys.forEach(key => {
            if (el[key] != null && key != "date") {
              field = key;
            }
          });
          el["value"] = el[field];
          el["field"] = field;
        });
        return ary;
      },
      includeNullDates() {
        for (let date = new Date(this.values[0].date); date > (new Date(this.values[this.values.length - 1].date).setYear(2018)); date.setDate(date.getDate() - 1)) {
          this.values.unshift({'date': date, 'test': 1})
        }
      }
    }
  };
</script>

<style scoped>
  .insightChartDiv {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;
    width: 100%;
    position: absolute;
    top: 30px;
  }
</style>

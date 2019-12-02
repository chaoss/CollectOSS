<template>
  <div ref="holder" class="insightChartDiv">
    <spinner v-if="!loaded" class="insightChartSpinner"></spinner>
    <!-- <div v-if="loaded" class=""> -->
    <vega-lite v-if="loaded" :spec="vegaSpec" :data="values" center="true"></vega-lite>
    <!-- <p> {{ chart }} </p> -->

    <!-- </div> -->
  </div>
</template>


<script>
import { mapState } from "vuex";
import AugurStats from "@/AugurStats.ts";
import Spinner from "../Spinner.vue";
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
    earliest () {
      if (!this.values[0]) return null
      let d = new Date(this.values[this.values.length - 1].date)
      console.log(d)
      d.setYear(d.getYear() - 1);
      return d
    },
    latest () {
      if (!this.values[0]) return null
      let d = new Date(this.values[this.values.length - 1].date)
      return d
    }
  },
  methods: {
    calculateVegaSpec() {
      this.loaded = false;
      console.log('inside calculate vega spec');
      let specWidth = this.$refs.holder.clientWidth * 0.75;
      let specHeight = this.$refs.holder.clientHeight * 0.75;
      this.values = this.data;
      this.includeNullDates()
      this.vegaSpec = {
        $schema: "https://vega.github.io/schema/vega-lite/v2.json",
        center: true, 
        width: specWidth, //263.7,
        height: specHeight, //166,
        padding: { left: specWidth * .1, top: 10, right: 0, bottom: 5 },
        layer: [
          {
            mark: {
              type: "line",
              interpolate: "basis"
            },
            encoding: {
              x: {
                timeUnit: "yearmonthdate",
                field: "date",
                type: "temporal",
                axis: { grid: false, format: "%b %d" }
                // domain: [this.earliest, this.latest]
              },
              y: {
                // "aggregate": "sum",
                field: "value",
                type: "quantitative",
                axis: { grid: false, title: false, ticks: false }
              },
              color: { value: this.color }
            }
          },
          {
            mark: {
              type: "line",
              interpolate: "basis"
            },
            encoding: {
              x: {
                timeUnit: "yearmonthdate",
                field: "date",
                type: "temporal",
                axis: { grid: false, format: "%b %d" }
                // domain: [this.earliest, this.latest]
              },
              y: {
                // "aggregate": "sum",
                field: "test",
                type: "quantitative",
                axis: { grid: false, title: false, ticks: false }
              },
              opacity: { value: 0 }
            }
          }
        ]
      };
      this.loaded = true;
    },
    renderChart() {},
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
    includeNullDates () {
      for (let date = new Date(this.values[0].date); date > (new Date(this.values[this.values.length - 1].date).setYear(2018)); date.setDate(date.getDate() - 1)){
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

<style lang="stylus"></style>
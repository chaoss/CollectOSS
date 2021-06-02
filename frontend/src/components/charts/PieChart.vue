<!-- #SPDX-License-Identifier: MIT -->
<template>

  <d-card-body :title="title" ref="holder">
    <div v-if="!loaded">
      <spinner></spinner>
    </div>
    <div :id="'chart' + field"></div>
  </d-card-body>
</template>

<script lang="ts">
import { mapState } from 'vuex'
import Vue from 'vue';
import vegaEmbed from 'vega-embed'
import Component from 'vue-class-component';
import AugurStats from '@/AugurStats.ts'
import Spinner from '../../components/Spinner.vue'
import {mapActions, mapGetters, mapMutations} from "vuex";

@Component({
  components: {
    Spinner,
  },
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'domain', 'data', 'field'], 
  methods: {
    ...mapActions('common',[
      'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                  // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
    ])
  },
  computed: {
    ...mapGetters('common',[

    ]),
    ...mapGetters('compare',[
      'base'
    ]),
  },
})
export default class PieChart extends Vue {

  //data props
  loaded: boolean = false
  // getters
  base!:any

  //props
  source!:any
  field!:any
  data!:any



  get spec() {


    //COLORS TO PICK FOR EACH REPO
    var colors = ["black", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]

    let config: any = {
      "$schema": "https://vega.github.io/schema/vega/v5.json",
      "width": 200,
      "height": 200,
      "autosize": "none",

      "signals": [
        {
          "name": "startAngle", "value": 0,
          // "bind": {"input": "range", "min": 0, "max": 6.29, "step": 0.01}
        },
        {
          "name": "endAngle", "value": 6.29,
          // "bind": {"input": "range", "min": 0, "max": 6.29, "step": 0.01}
        },
        {
          "name": "padAngle", "value": 0,
          // "bind": {"input": "range", "min": 0, "max": 0.1}
        },
        {
          "name": "innerRadius", "value": 60,
          // "bind": {"input": "range", "min": 0, "max": 90, "step": 1}
        },
        {
          "name": "cornerRadius", "value": 0,
          // "bind": {"input": "range", "min": 0, "max": 10, "step": 0.5}
        },
        {
          "name": "sort", "value": false,
          "bind": {"input": "checkbox"}
        }
      ],

      "data": [
        {
          "name": "table",
          "transform": [
            {
              "type": "pie",
              "field": this.field,
              "startAngle": {"signal": "startAngle"},
              "endAngle": {"signal": "endAngle"},
              "sort": {"signal": "sort"}
            }
          ]
        }
      ],

      "legends": [
        {
          "stroke": "color",
          "title": "Author Email",
          "padding": 4,
          "encode": {
            "symbols": {
              "enter": {
                "strokeWidth": {"value": 2},
                "size": {"value": 50}
              }
            }
          }
        }
      ],

      "scales": [ //{"scale": "r", "field": "data"},
        {
          "name": "color",
          "type": "ordinal",
          "domain": {"data": "table", "field": "email"},
          "range": {"scheme": "category10"}
        },
        {
          "name": "r",
          "type": "sqrt",
          "domain": {"data": "table", "field": this.field},
          "zero": true,
          "range": [20, 100]
        }
      ],

      "marks": [
        {
          "type": "arc",
          "from": {"data": "table"},
          "encode": {
            "enter": {
              "fill": {"scale": "color", "field": "email"},
              "x": {"signal": "width / 2"},
              "y": {"signal": "height / 2"}
            },
            "update": {
              "startAngle": {"field": "startAngle"},
              "endAngle": {"field": "endAngle"},
              "padAngle": {"signal": "padAngle"},
              "innerRadius": {"signal": "innerRadius"},
              "outerRadius": {"signal": "width / 2"},//{"scale": "r", "field": "data"},
              "cornerRadius": {"signal": "cornerRadius"}
            }
          }
        },
        {
          "type": "text",
          "from": {"data": "table"},
          "encode": {
            "x": {"field": {"group": "width"}, "mult": 0.5},
            "y": {"field": {"group": "height"}, "mult": 0.5},
            "radius": {"scale": "r", "field": this.field, "offset": 8},
            "theta": {"signal": "(datum.startAngle + datum.endAngle)/2"},
            "fill": {"value": "#030"},
            "align": {"value": "center"},
            "baseline": {"value": "middle"},
            "text": {"field": this.field}
          }
        }
      ]
    }

    //define function that does any operation needed on data before sending it to the chart
    let processData = (data: any) => {

      console.log("PIECHART data",data)

      let values = []
      for (let i = 0; i < 10; i++) {
        data[i].id = data[i].email
      }

      //data reorganizing
      config.data[0].values = data
      this.loaded = true
      this.reloadImage(config)
    }

    //condition handler to retrieve data if needed and call processData with it
    if (!this.data) {
      // hitting endpoint
      this.base[this.source]().then((data: any) => {
        //data handler (what gets returned)
        
        processData(data)
      }, () => {
        //this.renderError()
      })
    } else {
      processData(this.data)
    }

    
    

    return config
    
  }

  reloadImage (config:any) {
    //,tooltip: {theme: 'dark'}
    console.log("piechart", JSON.stringify(config))
    vegaEmbed('#chart' + this.field, config, {actions: false}) 
  }

  mounted () {
    this.spec;
  }
}
</script>

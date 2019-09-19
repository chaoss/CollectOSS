<template>

  <div ref="holder">
    <div id="vis"></div>
  </div>
</template>

<script lang="ts">
import { mapState } from 'vuex'
import Vue from 'vue';
import vegaEmbed from 'vega-embed'
import Component from 'vue-class-component';
import AugurStats from '@/AugurStats.ts'
import {mapActions, mapGetters, mapMutations} from "vuex";

@Component({
  props: ['source', 'citeUrl', 'citeText', 'title', 'disableRollingAverage', 'alwaysByDate', 'domain', 'data'], 
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

  values:any[] = []

  // getters
  base!:any

  //props
  source!:any


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
          "bind": {"input": "range", "min": 0, "max": 6.29, "step": 0.01}
        },
        {
          "name": "endAngle", "value": 6.29,
          "bind": {"input": "range", "min": 0, "max": 6.29, "step": 0.01}
        },
        {
          "name": "padAngle", "value": 0,
          "bind": {"input": "range", "min": 0, "max": 0.1}
        },
        {
          "name": "innerRadius", "value": 90,
          "bind": {"input": "range", "min": 0, "max": 90, "step": 1}
        },
        {
          "name": "cornerRadius", "value": 0,
          "bind": {"input": "range", "min": 0, "max": 10, "step": 0.5}
        },
        {
          "name": "sort", "value": false,
          "bind": {"input": "checkbox"}
        }
      ],

      "data": [
        {
          "name": "table",
          "values": [
            {"id": 1, "field": 4},
            {"id": 2, "field": 6},
            {"id": 3, "field": 10},
            {"id": 4, "field": 3},
            {"id": 5, "field": 7},
            {"id": 6, "field": 8}
          ],
          "transform": [
            {
              "type": "pie",
              "field": "field",
              "startAngle": {"signal": "startAngle"},
              "endAngle": {"signal": "endAngle"},
              "sort": {"signal": "sort"}
            }
          ]
        }
      ],

      "scales": [
        {
          "name": "color",
          "type": "ordinal",
          "domain": {"data": "table", "field": "id"},
          "range": {"scheme": "category20"}
        }
      ],

      "marks": [
        {
          "type": "arc",
          "from": {"data": "table"},
          "encode": {
            "enter": {
              "fill": {"scale": "color", "field": "id"},
              "x": {"signal": "width / 2"},
              "y": {"signal": "height / 2"}
            },
            "update": {
              "startAngle": {"field": "startAngle"},
              "endAngle": {"field": "endAngle"},
              "padAngle": {"signal": "padAngle"},
              "innerRadius": {"signal": "innerRadius"},
              "outerRadius": {"signal": "width / 2"},
              "cornerRadius": {"signal": "cornerRadius"}
            }
          }
        }
      ]
    }



    let processData = (data: any) => {

      //data reorganizing

      config.data = {"values": data}
      this.values = data

    }


    console.log("HEYEYYY", this.base, this.source[])
    this.base[this.source].then((data: any) => {
      console.log(data)
      processData(data)
    }, () => {
      //this.renderError()
    }) // end batch request

    
    this.reloadImage(config)

    return config
    
  }

  reloadImage (config:any) {
    //,tooltip: {theme: 'dark'}
    vegaEmbed('#' + this.source, config, {actions: false}) 
  }
  mounted () {
    this.spec;
  }
  created () {
      // this.endpoint({endpoints:[this.source],repos:[this.base]}).then((data:any) => {
      //   this.values = data
      //   console.log(data)
      // })
      // console.log("YOYOYO", this.base, this.source)
      // this.base[this.source]().then((data:any) => {
      //   console.log("hello",data)
      // })
  }
}
</script>

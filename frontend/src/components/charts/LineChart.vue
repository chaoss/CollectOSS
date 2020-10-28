<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>
      <vega-lite v-if="loaded" :encoding="encoding" :data="values" :width="340" :height="320" :mark="mark"></vega-lite>
    </d-card-body>
  </d-card>
</template>

<script lang="ts">
  import  { Component, Vue } from 'vue-property-decorator';
  import {mapActions, mapGetters} from "vuex";
  import Spinner from '@/components/Spinner.vue'

  const AppProps = Vue.extend({
    props: {
      title: String,
      data: Object,
      source: String,
      field: String,
      filedTime: String,
      fieldCount: String
    }
  })

  @Component({
    components: {
      Spinner
    },
    computed: {
      ...mapGetters('compare',[
        'comparedRepos',
        'base',
      ]),
    },
    methods: {
      ...mapActions('common',[
        'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                    // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
      ]),
    }
  })
  export default class LineChart extends AppProps{

    // data props
    loaded: boolean = false
    values: any[] = []

    // compare.getter
    base!:any
    comparedRepos!:any

    // common actions
    endpoint!:any

    created () {
      if (this.data) {
        this.loaded = true
        this.values = this.data[this.source]
      }
      
      else {
        this.endpoint({endpoints:[this.source],repos:[this.base]}).then((tuples:any) => {
          console.log("lineChart:: ", tuples, this.base)
          let ref = this.base.url || this.base.repo_name
          let values:any = []
          Object.keys(tuples[ref]).forEach((endpoint) => {
            console.log("lineChart:: ", ref, endpoint)
            values = tuples[ref][endpoint]
          })
          console.log("lineChart::  loaded", JSON.stringify(values))
          this.values = values
          this.loaded = true
          console.log(this.loaded, this.values)
          
        })
      }
    }

    // get values(){
    //   console.log(this.data[this.source])
    //   return this.data[this.source]
    // }

    get encoding() {
      return {
        x: {field: this.filedTime, type: 'temporal'},
        y: {field: this.fieldCount, type: 'quantitative'}
      }
    }

    get mark() {
      return 'line'
    }

  }
</script>

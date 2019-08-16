<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <vega-lite :encoding="encoding" :data="values" :width="340" :height="320" :mark="mark"></vega-lite>
    </d-card-body>
  </d-card>
</template>

<script lang="ts">
  import  { Component, Vue } from 'vue-property-decorator';
  import {mapActions, mapGetters} from "vuex";

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
    computed: {
      ...mapGetters('compare',[
        'comparedRepos',
        'baseRepo'
      ]),
    },
  })
  export default class LineChart extends AppProps{

    // compare.getter
    baseRepo!:any
    comparedRepos!:any

    get values(){
      console.log(this.data[this.baseRepo][this.source])
      return this.data[this.baseRepo][this.source]
    }
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

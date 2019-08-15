<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <span style="font-size:1.3em">{{count}}</span>
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
  export default class CountBlock extends AppProps{

    // compare.getter
    baseRepo!:any
    comparedRepos!:any


    get count(){
      return this.data[this.baseRepo][this.source][0][this.field]
    }

  }
</script>
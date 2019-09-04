<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
    <p v-if="!count">There is no fork count data for this repository</p>
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
        'base'
      ]),
    },
  })
  export default class CountBlock extends AppProps{

    // compare.getter
    base!:any
    comparedRepos!:any


    get count(){
      console.log(this.data)
      console.log("****************************************")
      console.log(this.source)
      return this.data[this.source][0][this.field]
    }

  }
</script>

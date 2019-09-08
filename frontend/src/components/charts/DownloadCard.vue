<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <p v-if="values === undefined">There is no SBOM Download available for this repository.</p>
      <button v-if="values" @click="download">
        Download SBOM
      </button>
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
      headers: Array,
      fields: Array,
    }
  })

  @Component({
    computed: {
      ...mapGetters('compare',[
        'comparedRepos',
        'base'
      ]),
    },
    methods: {
      download(e) {
      console.log(this.values[0])
      let blob = new Blob([this.values[0].sbom_scan], { type: 'text/json' })
      let link = document.createElement('a')
      console.log(blob)
      link.href = window.URL.createObjectURL(blob)
      link.download = 'sbom.json'
      link.click()
      }
    }
  })
  export default class CountBlock extends AppProps{

    // compare.getter
    base!:any
    comparedRepos!:any


    get values(){
      return this.data[this.source]
    }

  }
</script>

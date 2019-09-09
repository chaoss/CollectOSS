<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <p v-if="values === undefined">There is no SBOM download available for this repository.</p>
      <button v-if="values" @click="download" style="border-radius:6px;">
        <strong>Download SBOM (.json)</strong>
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
      var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.values[0]));
      let link = document.createElement('a')
      link.setAttribute("href",     dataStr     );
      link.setAttribute("download", "sbom_" + this.values[0]['sbom_scan']["SPDX Data"]['DocumentName'] + ".json");
      link.click();
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

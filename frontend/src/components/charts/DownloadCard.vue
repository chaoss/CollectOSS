<template>
  <d-card>
  <!--
  {{values[0]['sbom_scan']["Document Information"]['DocumentName']}}
  -->
    <d-card-body :title="title" class="text-center">
      <p v-if="values.length == 0 || values[0] === undefined">There is no SBOM download available for this repository.</p>
      <button v-if="values" @click="download" style="border-radius:6px;" :msg=values>
        <strong>Download (.json)</strong>
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
  })
  export default class CountBlock extends AppProps{

    // compare.getter
    base!:any
    comparedRepos!:any


    get values(){
      return this.data[this.source]
    }

    download(e: any) {
      var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.values[0]['sbom_scan']));
      let link = document.createElement('a')
      console.log(link)
      link.setAttribute("href",     dataStr     );
      console.log(link)
      link.setAttribute("download", "sbom_" + this.values[0]['sbom_scan']["Document Information"]['DocumentName'] + ".json");
      link.click();
    }

  }
</script>

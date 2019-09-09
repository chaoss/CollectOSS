<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <p v-if="values === undefined">There are no license coverage metrics available for this repository.</p>
      <div style="float:left;text-align:right;width:49%;">
        <p> Total Files
        <br> Files with Declared Licenses
        <br> License Coverage </p>
      </div>
      <div style="float:right;text-align:left;width:49%;">
        <strong>
          <p> {{this.values[0]['sbom_scan']['Coverage']['TotalFiles']}}
          <br> {{this.values[0]['sbom_scan']['Coverage']['DeclaredLicenseFiles']}}
          <br> {{this.values[0]['sbom_scan']['Coverage']['PercentTotalLicenseCoverage']}} </p>
        </strong>
      </div>
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

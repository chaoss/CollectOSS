<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>
      <div v-if="loaded">
        <p v-if="values.length == 0 || values == undefined">There are no license coverage metrics available for this repository.</p>
        <div v-else>
          <div class="coverageCardDiv1">
            <p> Total Files
            <br> Files with Declared Licenses
            <br> License Coverage </p>
          </div>
          <div class="coverageCardDiv2">
            <strong>
              <p> {{ values[0]['sbom_scan']['License Coverage']['TotalFiles'] }}
              <br> {{ values[0]['sbom_scan']['License Coverage']['DeclaredLicenseFiles'] }}
              <br> {{ values[0]['sbom_scan']['License Coverage']['PercentTotalLicenseCoverage'] }} </p>
            </strong>
          </div>
        </div>
      </div>

    </d-card-body>
  </d-card>
</template>

<script lang="ts">
  import Spinner from '@/components/Spinner.vue'
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
    components: {
      Spinner
    },
    computed: {
      ...mapGetters('compare',[
        'comparedRepos',
        'base'
      ]),
    },
    methods: {
      ...mapActions('common',[
        'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                    // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
      ]),
    }
  })
  export default class CountBlock extends AppProps{

    // data props
    loaded: boolean = false
    values: any[] = []

    // compare getters
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
          let ref = this.base.url || this.base.repo_name
          if (ref.includes('/'))
            ref = ref.split('/')[ref.split('/').length - 1]
          let values:any = []
          Object.keys(tuples[ref]).forEach((endpoint) => {
            values = tuples[ref][endpoint]
          })
          this.values = values
          console.log("Coverage card values", values, ref)
          this.loaded = true
        })
      }
    }

    download (e: any) {
      var dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(this.values[0]));
      let link = document.createElement('a')
      link.setAttribute("href",     dataStr     );
      link.setAttribute("download", "sbom_" + this.values[0]['sbom_scan']["SPDX Data"]['DocumentName'] + ".json");
      link.click();
    }

  }
</script>

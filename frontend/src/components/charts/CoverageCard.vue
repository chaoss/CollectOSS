<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!allLoaded"></spinner>
      <div v-if="allLoaded">
        <p v-if="values.length == 0 || values == undefined">There are no license coverage metrics available for this repository.</p>
        <div v-else>
          <p> <h4> {{ UsableValues[2] }}% </h4> </p>
          <div class="coverageCardDiv1">
            <p> Total Files
            <br> Files with Declared Licenses
            <br> Files without Licenses </p>
          </div>
          <div class="coverageCardDiv2">
            <strong>
              <p> {{ UsableValues[0] }}
              <br> {{ UsableValues[1] }}
              <br> {{ UsableValues[3] }} </p>
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
      datatwo: Object,
      sourcetwo: String,
      headers: Array,
      fields: Array,
    }
  })

  @Component({
    components: {
      Spinner
    },
    computed: {
      allLoaded: function() {
        // @ts-ignore
        if (this.loaded && this.loaded2) {
          return true
        }
        else {
          return false
        }
      },
      UsableValues: function() {
        let licenseCount = 0
        // @ts-ignore
        for (let el of this.valuestwo) {
          let shortname = el['short_name'];
          if (shortname != "No Assertion"){
            licenseCount += el["count"]
          }
        }
        // @ts-ignore
        const totalFiles = this.values[0]['sbom_scan']['License Coverage']['TotalFiles']
        let prepercent = licenseCount / totalFiles
        let percent = prepercent * 100
        let fixed = 2 || 0;
        fixed = Math.pow(10, fixed);
        let licenseCoverage = Math.floor(percent * fixed) / fixed;
        let differenceCount = totalFiles - licenseCount
        let arrayofV = [totalFiles, licenseCount, licenseCoverage, differenceCount]
        return arrayofV
      },
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
    loaded2: boolean = false
    values: any[] = []
    valuestwo: any[] = []

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

      if (this.datatwo) {
        this.loaded2 = true
        this.valuestwo = this.datatwo[this.sourcetwo]
      }
      else {
        this.endpoint({endpoints:[this.sourcetwo],repos:[this.base]}).then((tuples:any) => {
          let ref = this.base.url || this.base.repo_name
          if (ref.includes('/'))
            ref = ref.split('/')[ref.split('/').length - 1]
          let valuestwo:any = []
          Object.keys(tuples[ref]).forEach((endpoint) => {
            valuestwo = tuples[ref][endpoint]
          })
          this.valuestwo = valuestwo
          console.log("Coverage card valuestwo", valuestwo, ref)
          this.loaded2 = true
        })
      }

    }
  }
</script>

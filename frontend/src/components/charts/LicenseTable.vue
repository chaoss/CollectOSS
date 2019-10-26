<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
<<<<<<< Updated upstream
      <spinner v-if="!loaded"></spinner>
      <div v-if="loaded">
        <strong><p>Click on the names of highlighted licenses to learn more</p></strong>
        <table class="licenseTable">
          <thead class="bg-light">
            <th v-for="header in headers">{{header}}</th>
          </thead>
          <tbody>
            <tr v-for="el in values">
              <a v-bind:href="ldata[0][el['short_name']]" target="_blank">
                <td>{{el['short_name']}}</td>
              </a>
            </tr>
          </tbody>
        </table>
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
      ldata: Array,
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
          console.log("sbom", tuples, this.base)
          let ref = this.base.url || this.base.repo_name
          let values:any = []
          Object.keys(tuples[ref]).forEach((endpoint) => {
            console.log("sbom", ref, endpoint)
            values = tuples[ref][endpoint]
          })
          console.log("sbom loaded", JSON.stringify(values))
          this.values = values
          this.loaded = true
          console.log(this.loaded, this.values)

        })
      }
    }

  }
</script>

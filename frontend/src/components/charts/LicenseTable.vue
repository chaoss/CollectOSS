<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>
      <div v-if="loaded">
        <table class="licenseTable">
          <thead style="border:2pt solid #f7f7f7;" class="bg-light">
            <th v-for="header in headers">{{header}}</th>
          </thead>
          <tbody style="border:2pt solid #f7f7f7;" >
            <tr style="border-bottom:1.5pt solid #f7f7f7;" v-for="el in values">
            <a v-bind:href="ldata[0][el['short_name']]" target="_blank">
                <td>{{el['short_name']}}</td>
              </a>
                <td>
                  <div v-if="el['license_id'] < 500">
                    <a v-on:click="linfo(el['license_id'])">
                      {{el['count']}}
                    </a>
                  </div>
                  <div v-if="el['license_id'] >= 500">
                  <a :href="'http://localhost:5000/api/unstable/500/False/25151/25158/license-files'">
                    {{el['count']}}
                  </a>
                  </div>
                </td>
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
      linfo: function (e) {
      console.log("**********************")
      console.log(this.$store.state.common.apiRepos)
      let repoID = this.$store.state.common.apiRepos[0].repo_id;
      let groupID = this.$store.state.common.apiRepose[0].repo_group_id;
        fetch(`http://localhost:5000/api/unstable/" + e + "/True/${groupID}/${repoID}/license-files`)
          .then(res => res.json())
          .then(res => {
            console.log('LICENSE FILES');
            console.log(res);
        });
      }
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

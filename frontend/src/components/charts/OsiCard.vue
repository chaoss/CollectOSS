<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>
      <div v-if="loaded">
        <h4>{{ OSIpercent[0] }}%</h4>
        <p> <br>
        OSI Approved: <strong>{{ OSIpercent[1] }}</strong> <br>
        Not OSI Approved: <strong>{{ OSIpercent[2] }}</strong> <br>
        Total: <strong>{{ OSIpercent[3] }}</strong> <br>
        </p>
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

  import * as check from './OSIapproved.json';
  @Component({
    components: {
      Spinner,
      check
    },
    computed: {
        OSIpercent: function() {
          let tcount = 0
          let fcount = 0
          console.log("ELEMENT")
          console.log(check)
          for (let el of this.values) {
            let count = el['count'];
            let shortname = el['short_name'];
            let determin = check.default[shortname];
            if (determin === true){
              tcount += count
            } else if (determin === false) {
              fcount += count
            }
        }
      let bigcount = (tcount + fcount)
      let prepercent = tcount / (tcount + fcount)
      console.log(tcount + fcount)
      console.log(tcount)
      console.log(fcount)
      let percent = prepercent * 100
      let fixed = 2 || 0;
      fixed = Math.pow(10, fixed);
      percent = Math.floor(percent * fixed) / fixed;
      return [percent, tcount, fcount, bigcount]
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

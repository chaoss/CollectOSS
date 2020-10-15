<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>
      <div v-if="loaded">
        <p> <h4>{{ OSIpercent[0] }}%</h4> </p>
        <p> 
        OSI Approved: <strong>{{ OSIpercent[1] }}</strong> Files
        <a href="javascript:void(0)" v-on:click="list(true)">
            <br> View Approved Licenses
        </a> <br><br>
        Not OSI Approved: <strong>{{ OSIpercent[2] }}</strong>
        <a href="javascript:void(0)" v-on:click="list(false)">
            <br> View Non-Approved licenses
        </a>
        </p>
      </div>
    </d-card-body>
  </d-card>
</template>

<script lang="ts">
  import Spinner from '@/components/Spinner.vue'
  import  { Component, Vue } from 'vue-property-decorator';
  import {mapActions, mapGetters} from "vuex";
  import * as check from './OSIapproved.json';

  const AppProps = Vue.extend({
    props: {
      title: String,
      data: Object,
      source: String,
      headers: Array,
      fields: Array,
      ldata: Array
    }
  })

  @Component({
    components: {
      Spinner
    },
    computed: {
        OSIpercent: function() {
          let tcount = 0
          let fcount = 0
          console.log("ELEMENT")
          console.log(check)
          // @ts-ignore
          for (let el of this.values) {
              let count = el['count'];
              let shortname = el['short_name'];
              // @ts-ignore
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
    list: function(indi) {
      let oList = {}
      let i = 0
      // @ts-ignore
      for (let el of this.values) {
        let count = el['count'];
        let shortname = el['short_name'];
        // @ts-ignore
        let determin = check.default[shortname];
        if (determin === true && indi == true){
          // @ts-ignore
          oList[i] = shortname
          i += 1
        } else if (determin === false && indi == false) {
          // @ts-ignore
          oList[i] = shortname
          i += 1
        }
      }
      // @ts-ignore
      let type = window.performance.getEntriesByType("navigation")[0].type
      let apiData = JSON.parse(JSON.stringify(this.$store.state.common.apiRepos));
      console.log(oList)
      let uriContent = URL.createObjectURL(new Blob([JSON.stringify(oList, null, 2)], {type : 'text/json;charset=utf-8'}));
      let link = document.createElement('a');
      link.setAttribute('href', uriContent);
      if (type === "reload") {
        if (indi == true) {
          link.setAttribute('download', Object.keys(apiData)[0] + ".approved.licenses.json");
        } else {
          link.setAttribute('download', Object.keys(apiData)[0] + ".notapproved.licenses.json");
        }
      } else {
        if (indi == true) {
          link.setAttribute('download', Object.keys(apiData)[1] + ".approved.licenses.json");
        } else {
          link.setAttribute('download', Object.keys(apiData)[1] + ".notapproved.licenses.json");
        }
      }
      let event = new MouseEvent('click');
      link.dispatchEvent(event);
    },
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

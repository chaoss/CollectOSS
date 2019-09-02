<template>
  <d-container fluid class="main-content-container px-4">
    <d-breadcrumb style="margin:0; padding-top: 26px; padding-left: 0px">
      <d-breadcrumb-item :active="false" :text="base.rg_name" href="#" />
      <d-breadcrumb-item :active="true" :text="base.repo_name" href="#" />
    </d-breadcrumb>
    <compare-control></compare-control>



    <!-- Overview Section -->
    <div class="page-header row no-gutters py-4" >
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <!-- <span class="text-uppercase page-subtitle">Components</span> -->
        <h3 class="page-title" style="font-size: 1rem">Risk</h3>
      </div>
    </div>

    <div class="row">
      <div v-if="!loaded_risk" class="col-md-12 col-lg-12">
        <spinner style="padding: 1rem 0 1rem 0; position: relative; transform: translateY(-50%);"></spinner>
      </div>
    </div>

    <div class="row mb-5" v-if="loaded_risk">
      <div class="col-6">
        <line-chart title="Forks Count by Week" :data="values" source="getForks" filedTime="date" fieldCount="forks">
        </line-chart>
      </div>
      <div class="col-6">
        <line-chart title="Committers by week" :data="values" source="committers" filedTime="date"
                    fieldCount="count"></line-chart>
      </div>
    </div>

    <div class="row mb-5" v-if="loaded_risk">
      <div class="col-6">
        <license-table :data="values" source="licenseDeclared"  :headers="['Short Name','Note']"
                       :fields="['short_name','note']"  title="License Declared"></license-table>
      </div>
      <div class="col-6">
        <cii-table :data="values" source="ciiBP"  :headers="['Passing Status','Badge Level', 'Date']"
                       :fields="['achieve_passing_status', 'badge_level', 'date']"  title="CII Best Practices" v-if="loaded_cii"></cii-table>
        <br v-if="loaded_cii"> <br v-if="loaded_cii">
        <count-block title="Forks" :data="values" source="forkCount" field="forks"></count-block>
                             </div>

      </div>
    </div>

  </d-container>
</template>

<script lang="ts">
  import  { Component, Vue } from 'vue-property-decorator';
  import {mapActions, mapGetters} from "vuex";
  import Spinner from '@/components/Spinner.vue'

  import DualLineChart from '../components/charts/DualLineChart.vue'
  import CompareControl from '../components/common/CompareControl.vue'
  import CountBlock from "@/components/charts/CountBlock.vue";
  import LineChart from "@/components/charts/LineChart.vue";
  import LicenseTable from "@/components/charts/LicenseTable.vue";
  import CiiTable from "@/components/charts/CiiTable.vue";
  // import PieChart from "@/components/charts/PieChart.vue";
  import router from "@/router";

  @Component({
    components: {
      DualLineChart,
      Spinner,
      CompareControl,
      CountBlock,
      LineChart,
      LicenseTable,
      CiiTable
      // PieChart,
    },
    methods: {
      ...mapActions('common',[
        'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                    // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
      ])
    },
    computed: {
      ...mapGetters('common',[
      ]),
      ...mapGetters('compare',[
        'base'
      ]),
    },
  })
  export default class RiskMetrics extends Vue {
    colors = ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF", "#3cb44b", "#ffe119", "#f58231", "#911eb4", "#42d4f4", "#f032e6"]
    testTimeframes = ['past 1 month', 'past 3 months', 'past 2 weeks']
    repos = {}
    projects = []
    themes = ['dark', 'info', 'royal-blue', 'warning']
    project = null

    loaded_cii:boolean = false
    loaded_risk:boolean = false

    values:any = {}

    // deflare vuex action, getter, mutations
    groupsInfo!: any;
    getRepoGroups!: any;
    repo_groups!: any[];
    sortedRepoGroups!: any[];
    base!: any;
    // actions
    endpoint!: any;


    // endpoints
    risk_endpoints:any[] = ['forkCount', 'licenseDeclared', 'getForks', 'committers']
    cii_endpoint = ['ciiBP']

    created() {
      console.log('####', this.base)

      this.endpoint({endpoints:this.cii_endpoint,repos:[this.base]}).then((tuples:any) => {
        Object.keys(tuples[this.base.url]).forEach((endpoint) => {
          this.values[endpoint] = tuples[this.base.url][endpoint]
        })
        this.loaded_cii = true
      }),
      this.endpoint({endpoints:this.risk_endpoints,repos:[this.base]}).then((tuples:any) => {
        Object.keys(tuples[this.base.url]).forEach((endpoint) => {
          this.values[endpoint] = tuples[this.base.url][endpoint]
        })
        this.loaded_risk = true
      })

    }

  }
</script>

<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-container fluid class="main-content-container px-4">
    <d-breadcrumb class="riskMetrics">
      <d-breadcrumb-item :active="false" :text="base.rg_name" href="#" />
      <d-breadcrumb-item :active="true" :text="base.repo_name" href="#" />
    </d-breadcrumb>
    <compare-control></compare-control>

    <!-- Overview Section -->
    <div class="page-header row no-gutters py-4" >
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <!-- <span class="text-uppercase page-subtitle">Components</span> -->
        <h3 class="page-title riskMetricsHeader">Risk</h3>
      </div>
    </div>

    <div class="row mb-5">
      <div class="col-6">
        <line-chart
          title="Forks Count by Week"
          source="getForks"
          filedTime="date"
          fieldCount="forks">
        </line-chart>
      </div>
      <div class="col-6">
        <line-chart
          title="Committers by week"
          source="committers"
          filedTime="date"
          fieldCount="count"
        ></line-chart>
      </div>
    </div>

    <div class="row mb-5">
      <div class="col-6">
        <license-table
          source="licenseDeclared"
          :headers="['Short Name', 'Count']"
          :ldata="licenses"
          :fields="['short_name']"
          title="License Declared">
        </license-table>
        <br><br>
        <download-card
          v-if="loaded_sbom"
          title="SPDX Document"
          :data="values"
          source="sbom">
        </download-card>
      </div>
      <div class="col-6">
        <cii-table
          source="ciiBP"
          :headers="['Passing Status','Badge Level', 'Date']"
          :fields="['name', 'achieve_passing_status', 'badge_level', 'date']"
          title="CII Best Practices"
        ></cii-table>
        <br> <br>
        <count-block
          title="Forks"
          source="forkCount"
          field="forks"
        ></count-block>
        <br><br>
        <coverage-card
          title="License Coverage"
          source="sbom"
          sourcetwo="licenseDeclared"
        ></coverage-card>
        <br><br>
        <osi-card
          source="licenseDeclared"
          :headers="['Short Name', 'Count']"
          :ldata="licenses"
          :fields="['short_name']"
          title="Percent OSI-Approved Licenses by File">
        </osi-card>
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
  import DownloadCard from "@/components/charts/DownloadCard.vue";
  import CoverageCard from "@/components/charts/CoverageCard.vue";
  import OsiCard from "@/components/charts/OsiCard.vue";
  // import PieChart from "@/components/charts/PieChart.vue";
  import Licenses from "@/components/Licenses.json";
  import router from "@/router";

  @Component({
    components: {
      DualLineChart,
      Spinner,
      CompareControl,
      CountBlock,
      LineChart,
      LicenseTable,
      CiiTable,
      DownloadCard,
      CoverageCard,
      OsiCard
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
    licenses = Licenses

    loaded_cii:boolean = false
    loaded_sbom:boolean = false

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
    cii_endpoint = ['ciiBP']
    sbom_endpoint = ['sbom']

    created() {
      console.log('####', this.base)
      let ref = this.base.url || this.base.repo_name
      this.endpoint({endpoints:this.sbom_endpoint,repos:[this.base]}).then((tuples:any) => {
        Object.keys(tuples[ref]).forEach((endpoint) => {

          this.values[endpoint] = tuples[ref][endpoint]
          console.log("sbom data loaded", endpoint, ref, tuples)
        })
        this.loaded_sbom = true
      })
      this.endpoint({endpoints:this.cii_endpoint,repos:[this.base]}).then((tuples:any) => {
        Object.keys(tuples[ref]).forEach((endpoint) => {
          this.values[endpoint] = tuples[ref][endpoint]
          console.log("cii data loaded", endpoint, ref, tuples)
        })
        this.loaded_cii = true
      })

    }

    onTab(e: any) {
      console.log("onTab", e.target.value)
      this.$router.push({
        name: e.target.value, params: {repo: this.base.repo_name, group: this.base.rg_name}
      })
    }

  }
</script>

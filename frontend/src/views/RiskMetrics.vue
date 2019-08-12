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

    <div class="row mb-5" v-if="loaded_rsik_1">
      <div class="col-3">
        <count-block title="Forks" :data="values1" source="forkCount" field="forks"></count-block>
      </div>
    </div>

    <div class="row mb-5" v-if="loaded_rsik_2">
      <div class="col-6">
        <line-chart title="Forks Count by Week" :data="values2" source="getForks" filedTime="date" fieldCount="forks">
        </line-chart>
      </div>
      <div class="col-6">
        <line-chart title="Committers by week" :data="values2" source="committers" filedTime="date"
                    fieldCount="count"></line-chart>
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
  // import PieChart from "@/components/charts/PieChart.vue";
  import router from "@/router";

  @Component({
    components: {
      DualLineChart,
      Spinner,
      CompareControl,
      CountBlock,
      LineChart,
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

    loaded_rsik_1:boolean = false;
    loaded_rsik_2:boolean = false;

    values1 = {}
    values2 = {}

    // deflare vuex action, getter, mutations
    groupsInfo!: any;
    getRepoGroups!: any;
    repo_groups!: any[];
    sorted_repo_groups!: any[];
    base!: any;
    // actions
    endpoint!: any;


    // endpoints
    risk_endpoints_1 = ['forkCount']

    risk_endpoints_2 = ['getForks', 'committers']

    created() {
      this.endpoint({endpoints:this.risk_endpoints_1,repos:[this.base]}).then((tuples:any) => {
        this.values1 = tuples;
        this.loaded_rsik_1 = true
      })
      this.endpoint({endpoints:this.risk_endpoints_2,repos:[this.base]}).then((tuples:any) => {
        this.values2 = tuples;
        this.loaded_rsik_2 = true
      })

    }

  }
</script>


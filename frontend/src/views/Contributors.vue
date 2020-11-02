<template>
  <d-container fluid class="main-content-container px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="dashboardHeader page-title">Contributor Data</h3>
      </div>
    </div>

    <d-row>

      <d-col v-for="index in 4" :key="index" lg="6" md="6" sm="12" class="mb-4">

        <d-card class="card-small card-post card-post--1">

          <div style="min-height: 34.2px !important;" v-if="loading">
            <spinner class="dashboardSpinner"></spinner>
          </div>

          <d-card-body v-if="!loading">

            <div v-if="index === 1" id="new_contributors_bar">

            </div>
            <div v-if="index === 2" id="new_contributors_stacked_bar">

            </div>
            <div v-if="index === 3" id="returning_contributors_pie_chart">

            </div>
            <div v-if="index === 4" id="returing_contributors_stacked_bar">

            </div>

          </d-card-body>

        </d-card>

      </d-col>

    </d-row>

  </d-container>
</template>

<script lang="ts">
import { mapActions, mapGetters, mapMutations } from "vuex";
import Component from "vue-class-component";
import Vue from "vue";
import axios from "axios";
import * as Bokehjs from 'bokehjs';
import InsightChart from "../components/charts/InsightChart.vue";
import Spinner from "../components/Spinner.vue";
@Component({
  methods: {
    ...mapActions("common", []),
  },
  computed: {
    ...mapGetters("common", ["baseURL"]),
  },
  components: {
    InsightChart,
    Spinner,
  },
})
export default class ContributorsPage extends Vue {
  // Data properties
  colors: any = ["#FFC107", "#FF3647", "#159dfb", "#343a40"];
  themes: any = ["warning", "danger", "royal-blue", "dark"];
  api_calls: string[] = ["new_contributors_bar", "new_contributors_stacked_bar", "returning_contributors_pie_chart", "returning_contributors_stacked_bar"]
  paramaters: any = {repo_id: 25158, start_date: "2019-01-01", end_date: "2020-03-30", required_time: 365, required_contributions: 5, return_json: true,}
  responses: any = [];
  loading: boolean = true;
  errored: boolean = false;
  baseURL!: any;
  color_mapping: any = {};
  pageData: any = [];

  // colors: any = ["#FFC107", "#FF3647", "#159dfb", "#343a40"];
  // themes: any = ["warning", "danger", "royal-blue", "dark"];
  // pageData: any = [];
  // loading: boolean = true;
  // desiredTopInsights: number = 12;
  // errored: boolean = false;
  // Allow access to vuex getters
  // baseURL!: any;
  // Allow access to vuex actions
  // 'mounted' lifecycle hook
  // Gets ran right after component initialization, data collection should be handled here
  mounted() {
    console.log(this.baseURL);

    let api_end: string;

    for(api_end of this.api_calls){

      if(api_end != "returning_contributors_pie_chart"){
       
        (this.paramaters).group_by = "month";
      }

      axios.get(`http://localhost:5000/api/unstable/contributor_reports/${api_end}/`,{params: this.paramaters,})
        .then((response) => {
        console.log("Contributors Page Data: ", response);

        (this.responses).push(response.data);

        if(api_end === "returning_contributors_stacked_bar"){
          this.loading = false
        }

        return Bokehjs.embed.embed_item(response.data);
      }).catch(error => {
        console.log("Contributors Page Error: ", error);
        this.errored = true
        this.loading = false
      }).finally(() => this.loading = false)

      //console.log("Responses: ", this.responses);
      
    }

  

    







    // axios
    //   .get(
    //     "http://localhost:5000/api/unstable/contributor_reports/new_contributors_bar/",
    //     {
    //       params: {
    //         repo_id: 25158,
    //         start_date: "2019-01-01",
    //         end_date: "2020-03-30",
    //         required_time: 365,
    //         required_contributions: 5,
    //         return_json: true,
    //         group_by: "month",
    //       },
    //     }
    //   )
    //   .then((response) => {

    //   console.log("Contributors Page Data: ", response);
    //   this.pageData = response.data
    //   this.loading = false

    //   return Bokehjs.embed.embed_item(response.data);
    // }).catch(error => {
    //   console.log("Contributors page error: ", error)
    //   this.errored = true
    //   this.loading = false
    // }).finally(() => this.loading = false)
  }
  //Functions go here

}
</script>

<style scoped>

#new_contributors_bar{
  border: black 1px solid;
}

</style>

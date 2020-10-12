<template>
  <d-container fluid class="main-content-container px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <h3 class="dashboardHeader page-title">
          Contributor Data
        </h3>
      </div>
    </div>

    <d-row>
      <d-col
        v-for="(record, index) in pageData"
        :key="index"
        lg="4"
        md="4"
        sm="6"
        class="mb-4"
      >
        <d-card class="card-small card-post card-post--1">
          <div style="min-height: 34.2px !important;" v-if="loading">
            <spinner class="dashboardSpinner"></spinner>
          </div>

          <div class="card-post__image" v-if="!loading && !errored">
            <d-badge
              pill
              :class="[
                'card-post__category',
                'bg-' + themes[color_mapping[record['ri_metric']]],
              ]"
            >
              {{ record["ri_metric"] }} ({{ record["ri_field"] }})
            </d-badge>

            <insight-chart
              :url="record['repo_git']"
              :repo_id="record['repo_id']"
              :metric="record['ri_metric']"
              :repo_group_id="record['repo_group_id']"
              :color="colors[color_mapping[record['ri_metric']]]"
            >
            </insight-chart>
          </div>

          <d-card-body v-if="!loading">
            <h5 class="card-title">
              <a
                :id="index"
                href="#"
                @click="onGitRepo(record['repo_git'])"
                class="text-fiord-blue underline"
                >{{ record["repo_git"].substr(19) }}</a
              >
              <d-tooltip
                :target="'#' + index"
                container=".shards-demo--example--tooltip-01"
                placement="right"
                offset="10"
              >
                Click here to see an overview of this repository's metrics
              </d-tooltip>
            </h5>

            <p class="card-text d-inline-block mb-1 dashboardP">
              This repository had an anomaly
              {{ dateDifferenceInDays(record["ri_date"], Date.now()) }} days
              ago.
            </p>

            <d-row>
              <d-col cols="12" sm="5">
                <d-row>
                  <d-col cols="12" sm="12">
                    <d-button
                      :id="'ev' + index"
                      size="sm"
                      @click="onGitRepo(record['repo_git'])"
                      class="dashboardButton d-flex btn-white ml-auto mr-auto ml-sm-auto mr-sm-0 mt-3 mt-sm-0"
                      >Evolution &rarr;</d-button
                    >
                    <d-tooltip
                      :target="'#ev' + index"
                      container=".shards-demo--example--tooltip-01"
                      offset="20"
                    >
                      Click to see evolution metrics for this repo.
                    </d-tooltip>
                  </d-col>
                </d-row>
              </d-col>

              <!-- View Full Report -->
              <d-col cols="12" sm="7" class="dashboardCol">
                <d-row>
                  <p></p>
                  <d-col cols="12" sm="12">
                    <d-button
                      theme="secondary"
                      :id="'ri' + index"
                      size="sm"
                      @click="onRisk(record['repo_git'])"
                      class="dashboardButton d-flex btn-white ml-auto mr-auto ml-sm-auto mr-sm-0 mt-3 mt-sm-0"
                    >
                      Risk &rarr;
                    </d-button>
                    <d-tooltip
                      :target="'#ri' + index"
                      container=".shards-demo--example--tooltip-01"
                      placement="right"
                      offset="20"
                    >
                      Click to see risk metrics for this repo.
                    </d-tooltip>
                  </d-col>
                </d-row>
              </d-col>
            </d-row>
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
    axios
      .post(
        "http://localhost:5000/api/unstable/contributors/new_contributors_bar",
        {
          repo_id: "25502",
          start_date: "2018-01-01",
          end_date: "2020-01-01",
          group_by: "month",
          required_contributions: 5,
          required_time: 365,
          return_json: true,
        }
      )
      .then((response) => {
        // axios.get(this.baseURL + "api/unstable/frontend-insights-page").then(response => {
        console.log("Contributors page response: ", response);
        // Define this.color_mapping based on the unique metrics returned by endpoint
        for (let i = 0; i < response.data.length; i++) {
          if (
            !Object.keys(this.color_mapping).includes(
              response.data[i]["ri_metric"]
            )
          ) {
            this.color_mapping[response.data[i]["ri_metric"]] =
              (Math.min(this.colors.length, this.themes.length) % i) - 1;
          }
        }
        this.pageData = response.data;
        this.loading = false;
      })
      .catch((error) => {
        console.log("Contributors page error: ", error);
        this.errored = true;
        this.loading = false;
      })
      .finally(() => (this.loading = false));
  }
  getOwner(url: string) {
    let first = url.indexOf(".");
    let last = url.lastIndexOf(".");
    let domain = null;
    let owner = null;
    let repo = null;
    let extension = false;
    if (url.includes("https://")) {
      url = url.substr(8);
      console.log(url);
    }
    if (first == last) {
      //normal github
      domain = url.substring(0, first);
      owner = url.substring(url.indexOf("/") + 1, url.lastIndexOf("/"));
      repo = url.slice(url.lastIndexOf("/") + 1);
      return owner;
    } else if (url.slice(last) == ".git") {
      //github with extension
      domain = url.substring(0, first);
      extension = true;
      owner = url.substring(url.indexOf("/") + 1, url.lastIndexOf("/"));
      repo = url.substring(url.lastIndexOf("/") + 1, url.length - 4);
      return owner;
    } else {
      //gluster
      domain = url.substring(first + 1, last);
      owner = null; //url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
      repo = url.slice(url.lastIndexOf("/") + 1);
      return domain;
    }
  }
  getRepo(url: string) {
    let first = url.indexOf(".");
    let last = url.lastIndexOf(".");
    let domain = null;
    let owner = null;
    let repo = null;
    let extension = false;
    if (first == last) {
      //normal github
      domain = url.substring(0, first);
      owner = url.substring(url.indexOf("/") + 1, url.lastIndexOf("/"));
      repo = url.slice(url.lastIndexOf("/") + 1);
      return repo;
    } else if (url.slice(last) == ".git") {
      //github with extension
      domain = url.substring(0, first);
      extension = true;
      owner = url.substring(url.indexOf("/") + 1, url.lastIndexOf("/"));
      repo = url.substring(url.lastIndexOf("/") + 1, url.length - 4);
      return repo;
    } else {
      //gluster
      domain = url.substring(first + 1, last);
      owner = null; //url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
      repo = url.slice(url.lastIndexOf("/") + 1);
      return repo;
    }
  }
  getDirection(values: any[]) {
    let i = 0;
    for (i = 0; i < values.length; i++) {
      if (values[i].discovered) {
        break;
      }
    }
    if (values[i + 1]) {
      if (values[i + 1].value > values[i].value) return "arrow_upward";
      else return "arrow_downward";
    } else {
      return "-";
    }
  }
  dateDifferenceInDays(date1: any, date2: any) {
    let dt1 = new Date(date1);
    let dt2 = new Date(date2);
    return Math.floor(
      (Date.UTC(dt2.getFullYear(), dt2.getMonth(), dt2.getDate()) -
        Date.UTC(dt1.getFullYear(), dt1.getMonth(), dt1.getDate())) /
        (1000 * 60 * 60 * 24)
    );
  }
  onGitRepo(e: any) {
    console.log("onGitRepo: ", e);
    this.$router.push({
      name: "repo_overview",
      params: {
        group: e.rg_name,
        repo: e.repo_git,
        repo_group_id: e.repo_group_id,
        repo_id: e.repo_id,
      },
    });
  }
  onRisk(e: any) {
    console.log("onRisk: ", e);
    this.$router.push({
      name: "repo_risk",
      params: {
        group: e.rg_name,
        repo: e.repo_git,
        repo_group_id: e.repo_group_id,
        repo_id: e.repo_id,
      },
    });
  }
  onInspectInsight(e: any) {
    console.log("onInspectInsight: ", e);
    this.$router.push({
      name: "inspect_insight",
      params: {
        group: e.rg_name,
        repo: e.repo_git,
        repo_group_id: e.repo_group_id,
        repo_id: e.repo_id,
        metric: e.ri_metric,
      },
    });
  }
  onRepoGroup(e: any) {
    console.log("onRepoGroup: ", e);
    this.$router.push({
      name: "group_overview",
      params: {
        group: e.rg_name,
        repo: e.repo_git,
        repo_group_id: e.repo_group_id,
        repo_id: e.repo_id,
      },
    });
  }
}
</script>

<style scoped></style>

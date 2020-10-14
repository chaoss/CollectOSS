<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-container fluid class="main-content-container px-4">
    <d-breadcrumb class="repo_Overview">
      <d-breadcrumb-item
        :active="false"
        :text="base.rg_name"
        href="#"
        @click="onRepoGroup({rg_name: base.rg_name, repo_group_id: base.repo_group_id})"
      />
      <d-breadcrumb-item :active="true" :text="base.repo_name" href="#" />
      <!-- <d-button style="line-height:1;transform: translateX(0.5rem) translateY(-0.1rem);"><d-link :to="{name: 'repo_risk', params: {repo: base.repo_name, group:base.rg_name}}"><span>Risk</span></d-link></d-button> -->
    </d-breadcrumb>

    <!-- <tab-selector></tab-selector> -->

    <p></p>
    <!-- <d-nav :pills="true" id="repo_nav">
      <d-nav-item :active="true" class="active">Overview</d-nav-item>
      <d-nav-item><d-link :to="{name: 'repo_risk', params: {repo: base.repo_name, group:base.rg_name}}"><span>Risk</span></d-link></d-nav-item>
    </d-nav>-->

    <!-- Compare Control -->
    <compare-control></compare-control>

    <!-- Overview Section -->
    <!-- <div class="page-header row no-gutters py-4" >
    <div class="col-12 col-sm-4 text-center text-sm-left mb-0">-->
    <!-- <span class="text-uppercase page-subtitle">Components</span> -->
    <!-- <h3 class="page-title" style="font-size: 1rem">Overview</h3>
      </div>
    </div>-->

    <p></p>

    <d-row>
      <d-col cols="12" md="6" lg="6" sm="12">
        <d-card>
          <!-- :style="loaderPadding(loadedBars)" > -->

          <!-- look to add commit chart? -->
          <!--<div class="col col-12">
            <commit-chart source="changesByAuthor" :data="values['changesByAuthor']"></commit-chart>
          </div>-->

          <d-container>
            <d-row>
              <d-col style>
                <d-card-body
                  title="Lines of code added by the top 10 authors as Percentages - By Time Period"
                  class="text-center"
                >
                  <spinner v-if="!loadedBars"></spinner>

                  <normalized-stacked-bar-chart
                    v-if="loadedBars"
                    source="changesByAuthor1"
                    :data="values['changesByAuthor']"
                  ></normalized-stacked-bar-chart>
                </d-card-body>
              </d-col>
            </d-row>

            <d-row>
              <d-col style>
                <d-card-body title="Average Lines of Code Per Commit" class="text-center">
                  <spinner v-if="!loadedBars"></spinner>

                  <horizontal-bar-chart
                    v-if="loadedBars"
                    measure="lines"
                    title="Average Lines of Code Per Commit"
                    source="changesByAuthor2"
                    :data="values['changesByAuthor']"
                  ></horizontal-bar-chart>
                </d-card-body>
              </d-col>
            </d-row>

            <!-- <d-row>
              <d-col v-if="loadedBars" style="">
                <one-dimensional-stacked-bar-chart type="lines" title="Lines of Code Added by the top 10 Authors as Percentages - All Time" :data="values['changesByAuthor']"></one-dimensional-stacked-bar-chart>
              </d-col>
            </d-row>

            <d-row>
              <d-col v-if="loadedBars" style="">
                <one-dimensional-stacked-bar-chart type="commit" title="Commits by the top 10 Authors as Percentages - All Time" :data="values['changesByAuthor']"></one-dimensional-stacked-bar-chart>
              </d-col>
            </d-row>-->
          </d-container>
        </d-card>
      </d-col>
      <d-col cols="12" md="6" lg="6" sm="12">
        <!--       <d-row>
          <d-col>
            <d-card>
              <pie-chart
              title="Commits by User"
              source="contributorsCodeDevelopment"
              field="commits"
              ></pie-chart>
            </d-card>
          </d-col>
          <d-col>
            <d-card>
              <pie-chart
              title="Lines of Code by User"
              source="contributorsCodeDevelopment"
              field="lines_added"
              ></pie-chart>
            </d-card>
          </d-col>
        </d-row>

        <p></p>
        -->
        <coverage-card title="License Coverage" source="sbom" sourcetwo="licenseDeclared"></coverage-card>

        <p></p>

        <d-card>
          <d-card-body title="Lines of code added by the top 10 authors" class="text-center">
            <spinner v-if="!loadedBars"></spinner>

            <lines-of-code-chart
              v-if="loadedBars"
              :data="values['changesByAuthor']"
              class="repo_Overview_Chart"
            ></lines-of-code-chart>
          </d-card-body>
        </d-card>
      </d-col>
    </d-row>

    <!-- <d-row style="padding-top: 2rem">

      <d-col>
        <d-card>
          <d-card-body title="Lines of code added by the top 10 authors visualized" class="text-center">

            <spinner v-if="!loadedBars"></spinner>

            <tick-chart
              v-if="loadedBars"
              source="changesByAuthor5"
              :data="values['changesByAuthor']"
            ></tick-chart>

          </d-card-body>
        </d-card>
      </d-col>

    </d-row>

    <p></p>-->

    <d-row>
      <div class="col col-6 repo_Overview_Col">
        <d-card>
          <dynamic-line-chart
            filedTime="date"
            fieldCount="pull_requests"
            source="reviews"
            title="Reviews (Pull Requests) / Week"
            cite-url
            cite-text="Reviews"
            :smoothing="true"
          ></dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6 repo_Overview_Col">
        <d-card>
          <dynamic-line-chart
            filedTime="date"
            fieldCount="pull_requests"
            source="reviewsAccepted"
            title="Reviews (Pull Requests) Accepted / Week"
            cite-url
            cite-text="Reviews Accepted"
            :smoothing="true"
          ></dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6 repo_Overview_Col">
        <d-card>
          <dynamic-line-chart
            filedTime="date"
            fieldCount="pull_requests"
            source="reviewsDeclined"
            title="Reviews (Pull Requests) Declined / Week"
            cite-url
            cite-text="Reviews Declined"
            :smoothing="true"
          ></dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6 repo_Overview_Col">
        <d-card>
          <dynamic-line-chart
            filedTime="date"
            fieldCount="open_count"
            source="openIssuesCount"
            title="Open Issues / Week"
            cite-url
            cite-text="Open Issues"
            :smoothing="true"
          ></dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6 repo_Overview_Col">
        <d-card>
          <dynamic-line-chart
            filedTime="date"
            fieldCount="closed_count"
            source="closedIssuesCount"
            title="Closed Issues / Week"
            cite-url
            cite-text="Closed Issues"
            :smoothing="true"
          ></dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6 repo_Overview_Col">
        <d-card>
          <dynamic-line-chart
            filedTime="date"
            fieldCount="issues"
            source="issuesNew"
            title="New Issues / Week"
            cite-url
            cite-text="New Issues"
            :smoothing="true"
          ></dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6 repo_Overview_Col">
        <d-card>
          <dynamic-line-chart
            source="codeChanges"
            title="Code Changes (Commits) / Week"
            cite-url
            cite-text="Code Changes"
            filedTime="date"
            fieldCount="commit_count"
            :smoothing="true"
          ></dynamic-line-chart>
        </d-card>
      </div>

      <div class="col col-6 repo_Overview_Col">
        <d-card>
          <dynamic-line-chart
            source="codeChangesLines"
            title="Lines of Code Added / Week"
            cite-url
            cite-text="Code Changes Lines"
            filedTime="date"
            fieldCount="added"
            :smoothing="true"
          ></dynamic-line-chart>
        </d-card>
      </div>
    </d-row>
  </d-container>
</template>

<script lang="ts">
import { Component, Vue } from "vue-property-decorator";
import { mapActions, mapGetters } from "vuex";
import SparkChart from "../components/charts/SparkChart.vue";
import InsightChart from "../components/charts/InsightChart.vue";
import TickChart from "../components/charts/TickChart.vue";
import LinesOfCodeChart from "../components/charts/LinesOfCodeChart.vue";
import NormalizedStackedBarChart from "../components/charts/NormalizedStackedBarChart.vue";
import OneDimensionalStackedBarChart from "../components/charts/OneDimensionalStackedBarChart.vue";
import HorizontalBarChart from "../components/charts/HorizontalBarChart.vue";
import GroupedBarChart from "../components/charts/GroupedBarChart.vue";
import StackedBarChart from "../components/charts/StackedBarChart.vue";
import DynamicLineChart from "../components/charts/DynamicLineChart.vue";
import DualLineChart from "../components/charts/DualLineChart.vue";
import Spinner from "../components/Spinner.vue";
import CompareControl from "../components/common/CompareControl.vue";
import router from "@/router";
import BubbleChart from "../components/charts/BubbleChart.vue";
import TimeIntervalBarChart from "../components/charts/TimeIntervalBarChart.vue";
import TabSelector from "../components/TabSelector.vue";
import PieChart from "../components/charts/PieChart.vue";
import CoverageCard from "@/components/charts/CoverageCard.vue";
import LineChart from "@/components/charts/LineChart.vue";

@Component({
  components: {
    InsightChart,
    TickChart,
    LinesOfCodeChart,
    NormalizedStackedBarChart,
    OneDimensionalStackedBarChart,
    HorizontalBarChart,
    GroupedBarChart,
    DynamicLineChart,
    StackedBarChart,
    DualLineChart,
    Spinner,
    CompareControl,
    BubbleChart,
    TimeIntervalBarChart,
    PieChart,
    CoverageCard,
    LineChart,
    TabSelector
  },
  methods: {
    ...mapActions("common", [
      "endpoint" // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
      // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
    ]),
    ...mapActions("compare", ["addComparedRepo", "setBaseGroup"])
  },
  computed: {
    ...mapGetters("common", ["repoRelations"]),
    ...mapGetters("compare", ["base"])
  }
})
export default class RepoOverview extends Vue {
  colors = [
    "#343A40",
    "#24a2b7",
    "#159dfb",
    "#FF3647",
    "#4736FF",
    "#3cb44b",
    "#ffe119",
    "#f58231",
    "#911eb4",
    "#42d4f4",
    "#f032e6"
  ];
  barEndpoints = ["changesByAuthor"];
  testTimeframes = ["past 1 month", "past 3 months", "past 2 weeks"];
  repos = {};
  projects = [];
  themes = ["dark", "info", "royal-blue", "warning"];
  project = null;
  loaded_overview = false;
  loaded_evolution = false;
  loaded_issues = false;
  loaded_experimental = false;
  loaded_activity = false;
  values: { [key: string]: any } = { issuesClosed: [], changesByAuthor: [] };
  loadedBars = false;

  // deflare vuex action, getter, mutations
  groupsInfo!: any;
  getRepoGroups!: any;
  repo_groups!: any[];
  sortedRepoGroups!: any[];
  base!: any;
  // actions
  endpoint!: any;
  setBaseGroup!: any;

  created() {
    // let repo = null
    // if (this.base)
    //   repo = this.base
    // else repo = this.rout
    this.endpoint({ endpoints: this.barEndpoints, repos: [this.base] }).then(
      (tuples: any) => {
        let ref = this.base.url || this.base.repo_name;
        Object.keys(tuples[ref]).forEach(endpoint => {
          console.log(endpoint);
          this.values[endpoint] = tuples[ref][endpoint];
          console.log("lines data: ", this.values);
        });

        this.loadedBars = true;
      }
    );
  }

  onRepoGroup(repo_group: any) {
    this.setBaseGroup(repo_group).then((repo: any) => {
      this.$router.push({
        name: "group_overview",
        params: { group: repo_group.rg_name }
      });
    });
  }

  loaderPadding(loaded: any) {
    if (loaded) return "";
    else return "padding-top: 3rem";
  }
}
</script>

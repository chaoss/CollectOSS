<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <div class="overviewCard">
      <h2
        v-if="loaded"
        class="overviewCardHeader"
      >Project Overview: {{ project }}</h2>
      <p></p>
      <h2
        class="overviewCard repolisting"
        v-if="$store.state.comparedRepos.length > 0"
      >compared to:</h2>
      <h2 class="overviewCard" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting">{{ repo }}</span>
      </h2>
    </div>

    <div class="row overviewCardDiv" v-if="loaded">
      <div class="col col-6 overviewCardPadding">
        <grouped-bar-chart
          source="annualCommitCountRankedByRepoInRepoGroup"
          title="Top Repos in 2018 by Commits with Baseline Averages - Sorted"
          field="commit"
          :data="values['annualCommitCountRankedByRepoInRepoGroup']"
        ></grouped-bar-chart>
      </div>
      <div class="col col-6 overviewCardPadding">
        <grouped-bar-chart
          source="annualLinesOfCodeCountRankedByRepoInRepoGroup"
          title="Top Repos in 2018 by Net LoC with Baseline Averages - Sorted"
          field="loc"
          :data="values['annualLinesOfCodeCountRankedByRepoInRepoGroup']"
        ></grouped-bar-chart>
      </div>
      <div class="col col-6 overviewCardPadding">
        <grouped-bar-chart
          source="annualCommitCountRankedByNewRepoInRepoGroup"
          title="Top New Repos in 2018 by Commits with Baseline Averages - Sorted"
          field="commit"
          :data="values['annualCommitCountRankedByNewRepoInRepoGroup']"
        ></grouped-bar-chart>
      </div>
      <div class="col col-6 overviewCardPadding">
        <grouped-bar-chart
          source="annualLinesOfCodeCountRankedByNewRepoInRepoGroup"
          title="Top New Repos in 2018 by Net LoC with Baseline Averages - Sorted"
          field="loc"
          :data="values['annualLinesOfCodeCountRankedByNewRepoInRepoGroup']"
        ></grouped-bar-chart>
      </div>
    </div>
  </section>
</template>

<script>
import AugurHeader from "./AugurHeader"
import TickChart from "./charts/TickChart"
import LinesOfCodeChart from "./charts/LinesOfCodeChart"
import NormalizedStackedBarChart from "./charts/NormalizedStackedBarChart"
import OneDimensionalStackedBarChart from "./charts/OneDimensionalStackedBarChart"
import HorizontalBarChart from "./charts/HorizontalBarChart"
import GroupedBarChart from "./charts/GroupedBarChart"
import StackedBarChart from "./charts/StackedBarChart"
import TimeIntervalBarChart from './charts/TimeIntervalBarChart'
export default {
  data() {
    return {
      colors: [
        "#FF3647",
        "#4736FF",
        "#3cb44b",
        "#ffe119",
        "#f58231",
        "#911eb4",
        "#42d4f4",
        "#f032e6"
      ],
      values: {},
      loaded: false,
      project: null
    };
  },
  components: {
    AugurHeader,
    TickChart,
    LinesOfCodeChart,
    NormalizedStackedBarChart,
    OneDimensionalStackedBarChart,
    HorizontalBarChart,
    GroupedBarChart,
    StackedBarChart,
    TimeIntervalBarChart
  },
  computed: {
    repo() {
      return this.$store.state.baseRepo;
    },
    gitRepo() {
      return this.$store.state.gitRepo;
    },
    comparedRepos() {
      return this.$store.state.comparedRepos;
    }
    // loaded() {
    //   return this.loaded1 && this.loaded2
    // }
  },
  created() {
    let repos = [];
    if (this.repo) {
      if (window.AugurRepos[this.repo])
        repos.push(window.AugurRepos[this.repo]);
      // repos.push(this.repo)
    } // end if (this.$store.repo)
    this.comparedRepos.forEach(function(repo) {
      repos.push(window.AugurRepos[repo]);
    });
    let endpoints1 = [
      "annualLinesOfCodeCountRankedByRepoInRepoGroup",
      "annualCommitCountRankedByRepoInRepoGroup",
      "annualLinesOfCodeCountRankedByNewRepoInRepoGroup",
      "annualCommitCountRankedByNewRepoInRepoGroup",
      "facadeProject"
    ];
    endpoints1.forEach(source => {
      let repo = window.AugurAPI.Repo({ gitURL: this.gitRepo });
      repo[source]().then(
        data => {
          console.log("batch data", data);
          this.values[source] = data;
          this.loaded = true;
          this.project = this.values["facadeProject"][0].name;
          console.log(this.project, "here", this.values["facadeProject"]);
        },
        () => {
          //this.renderError()
        }
      ); // end batch request
    });
  }
};
</script>
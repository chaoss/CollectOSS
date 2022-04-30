<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <div class="baseRepo">
      <h2 class="gitCardHeader2">{{ $store.state.gitRepo }}</h2>
      <h2
        class="repolisting gitCardHeader"
        v-if="$store.state.comparedRepos.length > 0"
      >
        compared to:
      </h2>
      <h2
        class="gitCardHeader"
        v-for="(repo, index) in $store.state.comparedRepos"
        :key="index"
      >
        <span v-bind:style="{ color: colors[index] }" class="repolisting">
          {{ repo }}
        </span>
      </h2>
    </div>

    <div v-if="!loaded" class="gitCardDiv1 col col-12 spinner loader"></div>

    <div class="row gitCardDiv2" v-if="loaded">
      <div class="col col-12">
        <tick-chart
          source="changesByAuthor"
          :data="values['changesByAuthor']"
        ></tick-chart>
      </div>
      <!--<div class="col col-12">
          <commit-chart source="changesByAuthor" :data="values['changesByAuthor']"></commit-chart>
        </div> -->
      <div class="col col-6 gitCardDiv3">
        <normalized-stacked-bar-chart
          title="Lines of code added by the top 10 authors as Percentages - By Time Period"
          source="changesByAuthor1"
          :data="values['changesByAuthor']"
        >
        </normalized-stacked-bar-chart>
      </div>
      <div class="col col-6 gitCardDiv4">
        <div class="gitCardDiv5"></div>
        <horizontal-bar-chart
          measure="lines"
          title="Average Lines of Code Per Commit"
          source="changesByAuthor2"
          :data="values['changesByAuthor']"
        ></horizontal-bar-chart>
      </div>
    </div>
    <div class="gitCardDiv6 row" v-if="loaded">
      <div class="col col-6">
        <one-dimensional-stacked-bar-chart
          type="lines"
          title="Lines of Code Added by the top 10 Authors as Percentages - All Time"
        ></one-dimensional-stacked-bar-chart>
      </div>
      <div class="col col-6">
        <one-dimensional-stacked-bar-chart
          type="commit"
          title="Commits by the top 10 Authors as Percentages - All Time"
        ></one-dimensional-stacked-bar-chart>
      </div>
    </div>

    <div class="row gitCardDiv7" v-if="loaded">
      <lines-of-code-chart></lines-of-code-chart>
    </div>
  </section>
</template>

<script>
import AugurHeader from "./AugurHeader.vue";
import TickChart from "./charts/TickChart.vue";
import CommitChart from "./charts/CommitChart.vue";
import LinesOfCodeChart from "./charts/LinesOfCodeChart.vue";
import NormalizedStackedBarChart from "./charts/NormalizedStackedBarChart.vue";
import OneDimensionalStackedBarChart from "./charts/OneDimensionalStackedBarChart.vue";
import HorizontalBarChart from "./charts/HorizontalBarChart.vue";
import GroupedBarChart from "./charts/GroupedBarChart.vue";
import DirectionalTimeChart from "./charts/DirectionalTimeChart.vue";
import TimeIntervalBarChart from "./charts/TimeIntervalBarChart.vue";

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
        "#f032e6",
      ],
      values: {},
      loaded: false,
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
    DirectionalTimeChart,
    TimeIntervalBarChart,
    CommitChart,
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
    },
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
    this.comparedRepos.forEach(function (repo) {
      repos.push(window.AugurRepos[repo]);
    });
    let endpoints1 = ["changesByAuthor"];
    endpoints1.forEach((source) => {
      let repo = null;
      if (this.repo) {
        if (window.AugurRepos[this.repo]) {
          repo = window.AugurRepos[this.repo];
        } else {
          repo = window.AugurAPI.Repo({ gitURL: this.gitRepo });
          window.AugurRepos[repo.toString] = repo;
        }
      } else {
        repo = window.AugurAPI.Repo({ gitURL: this.gitRepo });
        window.AugurRepos[repo.toString()] = repo;
      }
      repo[source]().then(
        (data) => {
          console.log("batch data", data);
          this.values[source] = data;
          this.loaded = true;
        },
        () => {
          //this.renderError()
        }
      ); // end batch request
    });
  },
};
</script>
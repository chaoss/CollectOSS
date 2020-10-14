<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <!-- <h1>Growth, Maturity, and Decline</h1> -->
    <div class="growthMaturity">
      <h2 class="growthMaturityHeader">{{ $store.state.baseRepo }}</h2>
      <h2
        class=" growthMaturity repolisting"
        v-if="$store.state.comparedRepos.length > 0"
      >compared to:</h2>
      <h2 class="growthMaturity" v-for="(repo, index) in $store.state.comparedRepos">
        <span
          v-bind:style="{ 'color': colors[index] }"
          @click
          :value="repo"
          class="repolisting"
        >{{ repo }}</span>
      </h2>
    </div>
    <!-- <div class="row" v-if="loaded">
      <skeleton-chart source="openIssues"
                    title="Open Issues / Week"
                    cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    cite-text="Issues Open"
                    :data="values['openIssues']"></skeleton-chart>
    </div>-->

    <div v-if="loaded1" class="row">
      <div class="col col-6">
        <dynamic-line-chart
          source="codeReviewIteration"
          title="Number of Code Review Iterations"
          size="total"
          cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md"
          cite-text="Code Review Iterations"
          :data="values['codeReviewIteration']"
        ></dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart
          source="closedIssues"
          title="Closed Issues / Week"
          cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/closed-issues.md"
          cite-text="Issues Closed"
          :data="values['closedIssues']"
        ></dynamic-line-chart>
      </div>
    </div>

    <div v-if="loaded2" class="row">
      <div class="col col-6">
        <dynamic-line-chart
          source="contributionAcceptance"
          title="Contribution Acceptance"
          size="total"
          cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/contribution-acceptance.md"
          cite-text="Contribution Acceptance"
          :data="values['contributionAcceptance']"
        ></dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart
          source="forks"
          title="Forks / Week"
          cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/forks.md"
          cite-text="Forks"
          :data="values['forks']"
        ></dynamic-line-chart>
      </div>
    </div>

    <div v-if="loaded3" class="row">
      <div class="col col-6">
        <dynamic-line-chart
          source="maintainerResponseToMergeRequestDuration"
          title="Time to First Maintainer Response to Merge Request"
          size="total"
          cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md"
          cite-text="Time to First Maintainer Response to Merge Request"
          :data="values['maintainerResponseToMergeRequestDuration']"
        ></dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart
          source="codeCommits"
          title="Code Commits / Week"
          cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/commits.md"
          cite-text="Commits"
          :data="values['codeCommits']"
        ></dynamic-line-chart>
      </div>
    </div>

    <div v-if="loaded4" class="row">
      <div class="col col-6">
        <dynamic-line-chart
          source="newContributingGithubOrganizations"
          title="New Contributing Github Organizations"
          size="total"
          cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/new-contributing-organizations.md"
          cite-text="New Contributing Organizations"
          :data="values['newContributingGithubOrganizations']"
        ></dynamic-line-chart>
      </div>
      <div class="col col-6">
        <dynamic-line-chart
          source="openIssues"
          title="Open Issues / Week"
          cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/open-issues.md"
          cite-text="Issues Open"
          :data="values['openIssues']"
        ></dynamic-line-chart>
      </div>
    </div>
    <div v-if="loaded5" class="row">
      <div class="col col-6">
        <dynamic-line-chart
          source="pullRequestComments"
          title="Pull Request Comments / Week "
          cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/pull-request-comments.md"
          cite-text="Pull Request Comments"
          :data="values['pullRequestComments']"
        ></dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart
          source="pullRequestsOpen"
          title="Pull Requests Open / Week"
          cite-url="https://github.com/augurlabs/wg-gmd/blob/master/activity-metrics/pull-requests-open.md"
          cite-text="Open Pull Requests"
          :data="values['pullRequestsOpen']"
        ></dynamic-line-chart>
      </div>

      <div class="col col-12">
        <bubble-chart
          source="contributingGithubOrganizations"
          title="Contributing Github Organizations Overview"
          size="total"
          cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/contributing-organizations.md"
          cite-text="Contributing Organizations"
          :data="values['contributingGithubOrganizations']"
        ></bubble-chart>
      </div>
    </div>
    <div
      v-if="loaded == null"
      style="text-align: center; margin-left: 44.4%; position: relative !important"
      class="col col-12 spinner loader"
    ></div>

    <small>
      Data provided by
      <a href="http://ghtorrent.org/msr14.html">GHTorrent</a>
      <span class="ghtorrent-version"></span> and the
      <a href="https://developer.github.com/">GitHub API</a>
    </small>
  </section>
</template>

<script>
import BubbleChart from "./charts/BubbleChart";
import StackedBarChart from "./charts/StackedBarChart";
import DynamicLineChart from "./charts/DynamicLineChart";
import SkeletonChart from "./charts/SkeletonChart";
export default {
  components: {
    BubbleChart,
    StackedBarChart,
    DynamicLineChart,
    SkeletonChart
  },
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
      loaded1: null,
      loaded2: null,
      loaded3: null,
      loaded4: null,
      loaded5: null
    };
  },
  computed: {
    repo() {
      return this.$store.state.baseRepo;
    },
    gitRepos() {
      return this.$store.state.gitRepo;
    },
    comparedRepos() {
      return this.$store.state.comparedRepos;
    },
    loaded() {
      return (
        this.loaded1 &&
        this.loaded2 &&
        this.loaded3 &&
        this.loaded4 &&
        this.loaded5
      );
    }
  },
  methods: {
    getMetricsStatus() {
      var query_string =
        "group=" +
        this.selected_group +
        "&data_source=" +
        this.selected_source +
        "&metric_type=" +
        this.selected_metric_type +
        "&backend_status=" +
        this.selected_backend_status +
        "&frontend_status=" +
        this.selected_frontend_status +
        "&is_defined=" +
        this.selected_is_defined;

      window.AugurAPI.getMetricsStatus(query_string).then(data => {
        this.metricsData = data;
      });
    },
    removeComparison() {
      $(this.$el)
        .find(".multiselect__content-wrapper")
        .removeClass("selecting");
    }
  },
  mounted() {
    this.selected_group = "all";
    this.selected_source = "all";
    this.selected_metric_type = "all";
    this.selected_backend_status = "all";
    this.selected_frontend_status = "all";
    this.selected_is_defined = "all";
    this.getMetricsStatus();
  },
  created() {
    let repos = [];
    if (this.repo) {
      if (window.AugurRepos[this.repo])
        repos.push(window.AugurRepos[this.repo]);
      else if (this.domain) {
        let temp = window.AugurAPI.Repo({ gitURL: this.gitRepo });
        if (window.AugurRepos[temp]) temp = window.AugurRepos[temp];
        else window.AugurRepos[temp] = temp;
        repos.push(temp);
      }
      // repos.push(this.repo)
    } // end if (this.$store.repo)
    this.comparedRepos.forEach(function(repo) {
      repos.push(window.AugurRepos[repo]);
    });
    let endpoints1 = ["closedIssues", "codeReviewIteration"];
    window.AugurAPI.batchMapped(repos, endpoints1).then(
      data => {
        console.log("here", data);
        endpoints1.forEach(endpoint => {
          this.values[endpoint] = {};
          this.values[endpoint][this.repo] = {};
          this.values[endpoint][this.repo][endpoint] =
            data[this.repo][endpoint];
        });
        // this.values=data
        this.loaded1 = true;
        // return data
      },
      error => {
        this.loaded1 = false;
        console.log("failed", error);
      }
    ); // end batch request

    let endpoints2 = ["contributionAcceptance", "forks"];
    window.AugurAPI.batchMapped(repos, endpoints2).then(
      data => {
        console.log("here", data);
        endpoints2.forEach(endpoint => {
          this.values[endpoint] = {};
          this.values[endpoint][this.repo] = {};
          this.values[endpoint][this.repo][endpoint] =
            data[this.repo][endpoint];
        });
        // this.values=data
        this.loaded2 = true;
      },
      error => {
        this.loaded2 = false;
        console.log("failed", error);
      }
    ); // end batch request)

    let endpoints3 = [
      "codeCommits",
      "maintainerResponseToMergeRequestDuration"
    ];
    window.AugurAPI.batchMapped(repos, endpoints3).then(
      data => {
        console.log("here", data);
        endpoints3.forEach(endpoint => {
          this.values[endpoint] = {};
          this.values[endpoint][this.repo] = {};
          this.values[endpoint][this.repo][endpoint] =
            data[this.repo][endpoint];
        });
        // this.values=data
        this.loaded3 = true;
        // return data
      },
      error => {
        this.loaded3 = false;
        console.log("failed", error);
      }
    ); // end batch request

    let endpoints4 = ["newContributingGithubOrganizations", "openIssues"];
    window.AugurAPI.batchMapped(repos, endpoints4).then(
      data => {
        console.log("here", data);
        endpoints4.forEach(endpoint => {
          this.values[endpoint] = {};
          this.values[endpoint][this.repo] = {};
          this.values[endpoint][this.repo][endpoint] =
            data[this.repo][endpoint];
        });
        // this.values=data
        this.loaded4 = true;
        // return data
      },
      error => {
        this.loaded4 = false;
        console.log("failed", error);
      }
    ); // end batch request

    let endpoints5 = [
      "pullRequestComments",
      "pullRequestsOpen",
      "contributingGithubOrganizations"
    ];
    window.AugurAPI.batchMapped(repos, endpoints4).then(
      data => {
        console.log("here", data);
        endpoints5.forEach(endpoint => {
          this.values[endpoint] = {};
          this.values[endpoint][this.repo] = {};
          this.values[endpoint][this.repo][endpoint] =
            data[this.repo][endpoint];
        });
        // this.values=data
        this.loaded5 = true;
        // return data
      },
      error => {
        this.loaded5 = false;
        console.log("failed", error);
      }
    ); // end batch request
  }
};
</script>
<template>
  <section>
    <!-- <h1>Growth, Maturity, and Decline</h1> -->
    <div style="display: inline-block;">
      <h2 style="display: inline-block; color: black !important">{{ $store.state.baseRepo }}</h2>
      <h2 style="display: inline-block;" class="repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 style="display: inline-block;" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" @click="" :value="repo" class="repolisting"> {{ repo }} </span> 
      </h2>
    </div>
    <div class="row">

      <div class="col col-6">
        <dynamic-line-chart source="closedIssues"
                    title="Closed Issues / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Issues Closed">
        </dynamic-line-chart>
      </div>

      <!-- <div class="col col-6">
        <dynamic-line-chart source="closedIssueResolutionDuration"
                    title="Time to Close for Issue / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Issues Closed">
        </dynamic-line-chart>
      </div> -->

      <div class="col col-6">
        <dynamic-line-chart source="codeCommits"
                    title="Code Commits / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/commits.md"
                    cite-text="Commits">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="codeReviewIteration"
                      title="Number of Code Review Iterations"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md"
                      cite-text="Code Review Iterations">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="contributionAcceptance"
                      title="Contribution Acceptance"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/contribution-acceptance.md"
                      cite-text="Contribution Acceptance">
        </dynamic-line-chart>
      </div>

<!--       <div class="col col-6">
        <dynamic-line-chart source="firstResponseToIssueDuration"
                    title="Issue Response Time"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/issue-response-time.md"
                    cite-text="Issue Response Time">
        </dynamic-line-chart>
      </div>
 -->
      <div class="col col-6">
        <dynamic-line-chart source="forks"
                    title="Forks / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/forks.md"
                    cite-text="Forks">
        </dynamic-line-chart>
      </div>

<!--       <div class="col col-6">
        <dynamic-line-chart source="linesOfCodeChanged"
                    title="Lines Of Code Changed / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/lines-of-code-changed.md"
                    cite-text="Lines Of Code Changed">
        </dynamic-line-chart>
      </div>
 -->
      <div class="col col-6">
        <dynamic-line-chart source="maintainerResponseToMergeRequestDuration"
                      title="Time to First Maintainer Response to Merge Request"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md"
                      cite-text="Time to First Maintainer Response to Merge Request">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="newContributingGithubOrganizations"
                      title="New Contributing Github Organizations"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/new-contributing-organizations.md"
                      cite-text="New Contributing Organizations">
        </dynamic-line-chart>
      </div>

      <!-- <div class="col col-6">
        <dynamic-line-chart source="codeReviews"
                      title="Code Reviews"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-reviews.md"
                      cite-text="Code Reviews">
        </dynamic-line-chart>
      </div> -->

      <div class="col col-6">
        <dynamic-line-chart source="openIssues"
                    title="Open Issues / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    cite-text="Issues Open">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="pullRequestComments"
                    title="Pull Request Comments / Week "
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-request-comments.md"
                    cite-text="Pull Request Comments">
        </dynamic-line-chart>
      </div>

      <div class="col col-6">
        <dynamic-line-chart source="pullRequestsOpen"
                    title="Pull Requests Open / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-requests-open.md"
                    cite-text="Open Pull Requests">
        </dynamic-line-chart>
      </div>

      <div class="col col-12">
        <bubble-chart source="contributingGithubOrganizations"
                      title="Contributing Github Organizations Overview"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/contributing-organizations.md"
                      cite-text="Contributing Organizations">
        </bubble-chart>
      </div>

    </div>

    <small>Data provided by <a href="http://ghtorrent.org/msr14.html">GHTorrent</a> <span class="ghtorrent-version"></span> and the <a href="https://developer.github.com/">GitHub API</a></small>
  </section>
</template>

<script>
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'
import DynamicLineChart from './charts/DynamicLineChart'
module.exports = {
  components: {
    BubbleChart,
    StackedBarChart,
    DynamicLineChart
  },
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
    }
  },
  methods: {
    getMetricsStatus() {
      var query_string = "group=" + this.selected_group +
                         "&data_source=" + this.selected_source +
                         "&metric_type=" + this.selected_metric_type +
                         "&backend_status=" + this.selected_backend_status +
                         "&frontend_status=" + this.selected_frontend_status +
                         "&is_defined=" + this.selected_is_defined

        window.AugurAPI.getMetricsStatus(query_string).then((data) => {
          this.metricsData = data
      })
    },
    removeComparison() {
      $(this.$el).find('.multiselect__content-wrapper').removeClass('selecting')
    }
  },
  mounted() {
    this.selected_group = 'all'
    this.selected_source = 'all'
    this.selected_metric_type = 'all'
    this.selected_backend_status = 'all'
    this.selected_frontend_status = 'all'
    this.selected_is_defined = 'all'
    this.getMetricsStatus()
  }
};
</script>
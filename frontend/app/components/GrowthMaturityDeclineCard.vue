<template>
  <section>
    <h1>Growth, Maturity, and Decline</h1>
    <h2>{{ $store.state.baseRepo }}</h2>
    <div class="row">

      <div class="col col-6">
        <line-chart source="closedIssues"
                    title="Closed Issues / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Issues Closed">
        </line-chart>
      </div>

      <!-- <div class="col col-6">
        <line-chart source="closedIssueResolutionDuration"
                    title="Time to Close for Issue / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Issues Closed">
        </line-chart>
      </div> -->

      <div class="col col-6">
        <line-chart source="codeCommits"
                    title="Code Commits / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/commits.md"
                    cite-text="Commits">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="codeReviewIteration"
                      title="Number of Code Review Iterations"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md"
                      cite-text="Code Review Iterations">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="contributionAcceptance"
                      title="Contribution Acceptance"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/contribution-acceptance.md"
                      cite-text="Contribution Acceptance">
        </line-chart>
      </div>

<!--       <div class="col col-6">
        <line-chart source="firstResponseToIssueDuration"
                    title="Issue Response Time"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/issue-response-time.md"
                    cite-text="Issue Response Time">
        </line-chart>
      </div>
 -->
      <div class="col col-6">
        <line-chart source="forks"
                    title="Forks / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/forks.md"
                    cite-text="Forks">
        </line-chart>
      </div>

<!--       <div class="col col-6">
        <line-chart source="linesOfCodeChanged"
                    title="Lines Of Code Changed / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/lines-of-code-changed.md"
                    cite-text="Lines Of Code Changed">
        </line-chart>
      </div>
 -->
      <div class="col col-6">
        <line-chart source="maintainerResponseToMergeRequestDuration"
                      title="Time to First Maintainer Response to Merge Request"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md"
                      cite-text="Time to First Maintainer Response to Merge Request">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="newContributingGithubOrganizations"
                      title="New Contributing Github Organizations"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/new-contributing-organizations.md"
                      cite-text="New Contributing Organizations">
        </line-chart>
      </div>

      <!-- <div class="col col-6">
        <line-chart source="codeReviews"
                      title="Code Reviews"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-reviews.md"
                      cite-text="Code Reviews">
        </line-chart>
      </div> -->

      <div class="col col-6">
        <line-chart source="openIssues"
                    title="Open Issues / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    cite-text="Issues Open">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullRequestComments"
                    title="Pull Request Comments / Week "
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-request-comments.md"
                    cite-text="Pull Request Comments">
        </line-chart>
      </div>

      <div class="col col-6">
        <line-chart source="pullRequestsOpen"
                    title="Pull Requests Open / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-requests-open.md"
                    cite-text="Open Pull Requests">
        </line-chart>
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
import LineChart from './charts/LineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'
module.exports = {
  components: {
    LineChart,
    BubbleChart,
    StackedBarChart
  }
};
</script>

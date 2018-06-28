<template>
  <section>
    <h1>Growth, Maturity, and Decline</h1>
    <h2>{{ $store.state.baseRepo }}</h2>
    <div class="row">

      <div class="col col-6">
        <area-line-chart source="issues"
                    title="Issues / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    cite-text="Issues Open">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="issuesClosed"
                    title="Issues Closed / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Issues Closed">
        </area-line-chart>
      </div>

      <!-- <div class="col col-6">
        <area-line-chart source="issuesResponseTime"
                    title="Issue Response Time"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/issue-response-time.md"
                    cite-text="Issue Response Time">
        </area-line-chart>
      </div> -->

      <div class="col col-6">
        <area-line-chart source="commits"
                    title="Commits / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/commits.md"
                    cite-text="Commits">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="forks"
                    title="Forks / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/forks.md"
                    cite-text="Forks">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="pulls"
                    title="Pulls / Week"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-requests-open.md"
                    cite-text="Open Pull Requests">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="pullReqComments"
                    title="Pull Request Comments / Week "
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-request-comments.md"
                    cite-text="Pull Request Comments">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="codeReviewIteration"
                      title="Number of Code Review Iterations"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-review-iteration.md"
                      cite-text="Code Review Iterations">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="maintainerResponseTime"
                      title="Time to First Maintainer Response to Merge Request"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/maintainer-response-to-merge-request-duration.md"
                      cite-text="Time to First Maintainer Response to Merge Request">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="contributionAcceptance"
                      title="Contribution Acceptance"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/contribution-acceptance.md"
                      cite-text="Contribution Acceptance">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="newContributingGithubOrganizations"
                      title="New Contributing Github Organizations"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/new-contributing-organizations.md"
                      cite-text="New Contributing Organizations">
        </area-line-chart>
      </div>

      <!-- <div class="col col-6">
        <area-line-chart source="codeReviews"
                      title="Code Reviews"
                      size="total"
                      cite-url="https://github.com/chaoss/metrics/blob/master/activity-metrics/code-reviews.md"
                      cite-text="Code Reviews">
        </area-line-chart>
      </div> -->

      <div class="col col-12">
        <bubble-chart source="contributors"
                      title="Contributior Overview"
                      size="total"
                      cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/contributors.md"
                      cite-text="Contributors">
        </bubble-chart>
      </div>
<!--
      <div class="col col-6">
        <area-line-chart source="communityEngagement:issues_open"
                    title="Open Issues"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/open-issues.md"
                    cite-text="Open Issues"
                    disable-rolling-average=1>
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="communityEngagement:issues_closed_total"
                    title="Closed Issues"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/closed-issues.md"
                    cite-text="Closed Issues"
                    disable-rolling-average=1>
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="issueComments"
                    title="Issue Comments / Week "
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/people-opening-issues.md"
                    cite-text="Issue Comments">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="commitComments"
                    title="Commit Comments / Week "
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/code-reviews.md"
                    cite-text="Code Reviews (naive implementation)">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="pullReqComments"
                    title="Pull Request Comments / Week "
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-request-comments.md"
                    cite-text="Pull Request Comments">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="pullsAcceptanceRate"
                    title="Pull Request Acceptance Rate"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/pull-requests-made-closed.md"
                    cite-text="Pull Requets Made / Closed">
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="area-linesChanged:total_area-lines"
                    title="Size of Code Base"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/size-of-code-base.md"
                    cite-text="Size of Code Base"
                    disableRollingAverage=1>
        </area-line-chart>
      </div>

      <div class="col col-6">
        <area-line-chart source="totalCommitters"
                    title="Total Committers"
                    cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/contributors.md"
                    cite-text="Contributors"
                    disableRollingAverage=1>
        </area-line-chart>
      </div>

      <div class="col col-12">
        <bubble-chart source="contributors"
                      title="Contributior Overview"
                      size="total"
                      cite-url="https://github.com/OSSHealth/wg-gmd/blob/master/activity-metrics/contributors.md"
                      cite-text="Contributors">
        </bubble-chart>
      </div>
-->


    </div>

    <small>Data provided by <a href="http://ghtorrent.org/msr14.html">GHTorrent</a> <span class="ghtorrent-version"></span> and the <a href="https://developer.github.com/">GitHub API</a></small>
  </section>
</template>

<script>

import LineChart from './charts/LineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'
import AreaLineChart from './charts/AreaLineChart'

module.exports = {
  components: {
    LineChart,
    BubbleChart,
    StackedBarChart,
    AreaLineChart
  }
};

</script>

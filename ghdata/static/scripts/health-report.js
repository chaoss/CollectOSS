/* SPDX-License-Identifier: MIT */

function GHDataReport(apiUrl) {
  apiUrl = apiUrl || '/';
  var owner = this.getParameterByName('owner');
  var repo = this.getParameterByName('repo');
  this.api = new GHDataAPIClient(apiUrl, owner, repo);
  this.buildReport();
}


GHDataReport.prototype.getParameterByName = function(name, url) {
    if (!url) {
      url = window.location.href;
    }
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
};

GHDataReport.prototype.buildReport = function () {
  if (this.api.owner && this.api.repo) {
    document.getElementById('repo-label').innerHTML = this.api.owner + ' / ' + this.api.repo;
    // Commits
    this.api.commitsByWeek().then(function (commits) {
      MG.data_graphic({
        title: "Commits/Week",
        data: MG.convert.date(commits, 'date', '%Y-%m-%dT%H:%M:%S.%LZ'),
        chart_type: 'point',
        least_squares: true,
        full_width: true,
        height: 300,
        color_range: ['#aaa'],
        x_accessor: 'date',
        y_accessor: 'commits',
        target: '#commits-over-time'
      });
    });

    // Stargazers
    this.api.stargazersByWeek().then(function (stargazers) {
      MG.data_graphic({
        title: "Stars/Week",
        data: MG.convert.date(stargazers, 'date', '%Y-%m-%dT%H:%M:%S.%LZ'),
        chart_type: 'point',
        least_squares: true,
        full_width: true,
        height: 300,
        color_range: ['#aaa'],
        x_accessor: 'date',
        y_accessor: 'watchers',
        target: '#stargazers-over-time'
      });
    });

    // Forks
    this.api.forksByWeek().then(function (forks) {
      MG.data_graphic({
        title: "Forks/Week",
        data: MG.convert.date(forks, 'date', '%Y-%m-%dT%H:%M:%S.%LZ'),
        chart_type: 'point',
        least_squares: true,
        full_width: true,
        height: 300,
        color_range: ['#aaa'],
        x_accessor: 'date',
        y_accessor: 'projects',
        target: '#forks-over-time'
      });
    });

    // Issues
    this.api.issuesByWeek().then(function (issues) {
      MG.data_graphic({
        title: "Issues/Week",
        data: MG.convert.date(issues, 'date', '%Y-%m-%dT%H:%M:%S.%LZ'),
        chart_type: 'point',
        least_squares: true,
        full_width: true,
        height: 300,
        color_range: ['#aaa'],
        x_accessor: 'date',
        y_accessor: 'issues',
        target: '#issues-over-time'
      });
    });

    // Pull Requests
    this.api.pullRequestsByWeek().then(function (pulls) {
      MG.data_graphic({
        title: "Pull Requests/Week",
        data: MG.convert.date(pulls, 'date', '%Y-%m-%dT%H:%M:%S.%LZ'),
        chart_type: 'point',
        least_squares: true,
        full_width: true,
        height: 300,
        color_range: ['#aaa'],
        x_accessor: 'date',
        y_accessor: 'pull_requests',
        target: '#pulls-over-time'
      });
    });
  }
};

var client = new GHDataReport();

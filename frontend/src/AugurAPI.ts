/* tslint:disable */
var $ = require('jquery')
var _ = require('lodash')

interface __reverseEndpointMap {
  [key: string]: any; // Add index signature
}

export default class AugurAPI {
  __downloadedGitRepos: Array<Object>
  _version: string
  _host: string
  __cache: any
  __timeout: any
  __pending: any
  getDownloadedGitRepos: any
  getRepos: any
  getRepoGroups: any
  openRequests: number
  getMetricsStatus: any
  getMetricsStatusMetadata: any
  __endpointMap: any;
  __reverseEndpointMap: {
    [key: string]: any// Add index signature
  };


  constructor(hostURL: string = 'http://' + window.location.host, version: string = '/api/unstable', autobatch: any = null) {
    this.__downloadedGitRepos = []

    this._version = version || '/api/unstable'
    this._host = hostURL || 'http://' + window.location.host
    this.__cache = {}
    this.__timeout = null
    this.__pending = {}

    this.getDownloadedGitRepos = this.__EndpointFactory('git/repos')
    this.getRepos = this.__EndpointFactory('repos')
    this.getRepoGroups = this.__EndpointFactory('repo-groups')

    this.openRequests = 0
    this.getMetricsStatus = this.__EndpointFactory('metrics/status/filter')
    this.getMetricsStatusMetadata = this.__EndpointFactory('metrics/status/metadata')
    this.__reverseEndpointMap = {}
  }

  // __autobatcher (url, params, fireTimeout) {
  //   if (this.__timeout !== null && !fireTimeout) {
  //     this.__timeout = setTimeout(() => {
  //       __autobatch(undefined, undefined, true)
  //     })
  //   }
  //   return new Promise((resolve, reject) => {
  //     if (fireTimeout) {
  //       let batchURL = this._host + this._version + '/batch'
  //       let requestArray = []
  //       Object.keys(this.__pending).forEach((key) => {
  //         requestArray.push({})
  //       })
  //       $.post(batchURL)
  //     }
  //   })
  // }

  __endpointURL(endpoint: string) {
    return '' + this._host + this._version + '/' + endpoint
  }

  __URLFunctionFactory(url: string) {
    var self = this
    return function (params: any, callback: any) {
      var cacheKey = window.btoa(url + JSON.stringify(params))
      self.openRequests++
      if (self.__cache[cacheKey]) {
        if (self.__cache[cacheKey].created_at > Date.now() - 1000 * 60) {
          return new Promise((resolve, reject) => {
            resolve(self.__cache[cacheKey].data)
          })
        }
      }
      return $.get(url, params).then((data: any) => {
        self.openRequests--
        self.__cache[cacheKey] = {
          created_at: Date.now(),
          data: data
        }
        return data
      })
    }
  }

  __EndpointFactory(endpoint: string) {
    return this.__URLFunctionFactory(this.__endpointURL(endpoint))
  }

  batch(endpoints: Array<String>) {
    let str = '[{"method": "GET", "path": "' + endpoints.join('"},{"method": "GET", "path": "') + '"}]'
    console.log(str)
    this.openRequests++
    let url = this.__endpointURL('batch')
    // Check cached
    if (this.__cache[window.btoa(url + endpoints.join(','))]) {
      if (this.__cache[window.btoa(url + endpoints.join(','))].created_at > Date.now() - 1000 * 60) {
        return new Promise((resolve, reject) => {
          resolve(this.__cache[window.btoa(url + endpoints.join(','))].data)
        })
      }
    }
    return $.ajax(url, {
      type: 'post',
      data: str,
      dataType: 'json',
      contentType: 'application/json'
    }).then((data: any) => {
      this.openRequests--
      // Save to cache
      this.__cache[window.btoa(url + endpoints.join(','))] = {
        created_at: Date.now(),
        data: data
      }
      return data
    })
  }

  batchMapped(repos: Array<AugurAPI>, fields: { forEach: (arg0: (field: any) => void) => void; }) {
    let endpoints: String[] | any[] = []
    let reverseMap: any = {}
    let processedData: any = {}
    repos.forEach((repo) => {
      // Array.prototype.push.apply(endpoints, repo.batch(fields, true))
      // _.assign(reverseMap, repo.__reverseEndpointMap)
      processedData[repo.toString()] = {}
      fields.forEach((field) => {
        console.log("endpoint_map: ", field, repo, repo.__endpointMap[field])
        endpoints.push(repo.__endpointMap[field])
        reverseMap[repo.__endpointMap[field]] = repo.__reverseEndpointMap[repo.__endpointMap[field]]
      })
    })
    console.log("before batch:", endpoints, reverseMap)
    return this.batch(endpoints).then((data: any) => {

      let newdat = new Promise((resolve, reject) => {
        if (Array.isArray(data)) {
          data.forEach((response) => {
            if (response.status === 200 && reverseMap[response.path]) {
              processedData[reverseMap[response.path].owner] = {}
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = []
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = JSON.parse(response.response)
              console.log("pdata after response", processedData, typeof (reverseMap[response.path].owner), typeof (reverseMap[response.path].name), JSON.parse(response.response), response.response)
            } else if (reverseMap[response.path]) {
              console.log('failed null')
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = null
            }
          })
          console.log(processedData)
          resolve(processedData)
        } else {
          reject(new Error('data-not-array'))
        }
      })
      console.log(newdat, "newdata")
      return newdat
    })
  }


  Repo(repo: any) {
    if (repo.githubURL) {
      let splitURL = repo.githubURL.split('/')
      if (splitURL.length < 3) {
        repo.owner = splitURL[0]
        repo.name = splitURL[1]
      } else {
        repo.owner = splitURL[3]
        repo.name = splitURL[4]
      }
    }

    if (repo.gitURL) {
      if (repo.gitURL.includes('github.com')) {
        let splitURL = repo.gitURL.split('/')
        repo.owner = splitURL[1]
        repo.name = splitURL[2].split('.')[0]
      } else {
        let splitURL = repo.gitURL.split('/')
        repo.owner = splitURL[0]
        repo.name = splitURL[1]
      }
    }

    if (repo.owner && repo.name) {
      if (repo.repo_id == null || repo.repo_group_id == null) {
        let res: any = []
        $.ajax({
          type: "GET",
          url: this._version + '/repos/' + repo.owner + '/' + repo.name,
          async: false,
          success: function (data: any) {
            res = data;
          }
        })
        repo.repo_id = res[0].repo_id
        repo.repo_group_id = res[0].repo_group_id
        repo.rg_name = res[0].rg_name
      }
    }

    repo.toString = () => {
      if (repo.owner && repo.name) {
        return repo.owner + '/' + repo.name
      } else {
        return JSON.stringify(repo)
      }
    }
    repo.__endpointMap = {}
    repo.__reverseEndpointMap = {}

    repo.getDownloadedStatus = () => {
      this.getDownloadedGitRepos().then((data: any) => {
        let rs = false
        data.forEach((gitURL: string) => {
          if (gitURL.includes('github.com')) {
            let splitURL = gitURL.split('/')
            let owner = splitURL[3]
            let name = splitURL[4].split('.')[0]
            if (repo.toString() === (owner + '/' + name)) {
              rs = true
            }
          }
        })
        return rs
      })
    }

    var __Endpoint = (r: any, name: string, url: string) => {
      r[name] = this.__URLFunctionFactory(url)
      return r[name]
    }

    var Endpoint = (r: any, name: string, endpoint: string) => {
      var fullEndpoint = this._version + '/' + repo.owner + '/' + repo.name + '/' + endpoint
      var url = this._host + fullEndpoint
      r.__endpointMap[name] = fullEndpoint
      r.__reverseEndpointMap[fullEndpoint] = { name: name, owner: repo.toString() }
      return __Endpoint(r, name, url)
    }

    var Timeseries = (r: any, jsName: string, endpoint: string) => {
      let func = Endpoint(r, jsName, 'timeseries/' + endpoint)
      // func.relativeTo = (baselineRepo:any, params:any, callback:any) => {
      //   var url = 'timeseries/' + endpoint + '/relative_to/' + baselineRepo.owner + '/' + baselineRepo.name
      //   return Endpoint(url)()
      // }
      return func
    }

    var GitEndpoint = (r: any, jsName: string, endpoint: string) => {
      var url = this.__endpointURL('git/' + endpoint + '/?repo_url_base=' + window.btoa(r.gitURL))
      return __Endpoint(r, jsName, url)
    }

    var addRepoMetric = (r: any, jsName: string, endpoint: string) => {
      var fullEndpoint = this._version + '/repo-groups/' + repo.repo_group_id + '/repos/' + repo.repo_id + '/' + endpoint
      var url = this.__endpointURL('repo-groups/' + repo.repo_group_id + '/repos/' + repo.repo_id + '/' + endpoint)
      var fullEndpoint = this._version + '/repo-groups/' + repo.repo_group_id + '/repos/' + repo.repo_id + '/' + endpoint
      r.__endpointMap[jsName] = fullEndpoint
      r.__reverseEndpointMap[fullEndpoint] = { name: jsName, owner: repo.toString() }
      return __Endpoint(r, jsName, url)
    }

    var addRepoGroupMetric = (r: any, jsName: string, endpoint: string) => {
      var url = this.__endpointURL('repo-groups/' + repo.repo_group_id + '/' + endpoint)
      var fullEndpoint = this._version + '/' + 'repo-groups/' + repo.repo_group_id + '/' + endpoint
      r.__endpointMap[jsName] = fullEndpoint
      r.__reverseEndpointMap[fullEndpoint] = { name: jsName, owner: repo.toString() }
      return __Endpoint(r, jsName, url)
    }

    repo.batch = (jsNameArray: Array<string>, noExecute: boolean) => {
      var routes = jsNameArray.map((e: any) => { return repo.__endpointMap[e] })
      if (noExecute) {
        return routes
      }
      return this.batch(routes).then((data: any) => {
        return new Promise((resolve, reject) => {
          if (Array.isArray(data)) {
            let mapped: { [key: string]: any } = {}
            console.log()
            data.forEach(response => {
              if (response.status === 200) {
                mapped[repo.__reverseEndpointMap[response.path].name] = JSON.parse(response.response)
                console.log('mapped:', mapped)
              } else {
                mapped[repo.__reverseEndpointMap[response.path].name] = null
                console.log('mapped null:', mapped, repo.__reverseEndpointMap[response.path])
              }
            })
            resolve(mapped)
          } else {
            console.log("didnt work")
            reject(new Error('data-not-array'))
          }
        })
      })
    }

    if (repo.owner && repo.name) {
      // DIVERSITY AND INCLUSION

      // GROWTH, MATURITY, AND DECLINE
      Timeseries(repo, 'closedIssues', 'issues/closed')
      Timeseries(repo, 'closedIssueResolutionDuration', 'issues/time_to_close')
      Timeseries(repo, 'codeCommits', 'commits')
      // Timeseries(repo, 'codeReviews', 'code_reviews')
      Timeseries(repo, 'codeReviewIteration', 'code_review_iteration')
      Timeseries(repo, 'contributionAcceptance', 'contribution_acceptance')
      Endpoint(repo, 'contributingGithubOrganizations', 'contributing_github_organizations')
      Timeseries(repo, 'firstResponseToIssueDuration', 'issues/response_time')
      Timeseries(repo, 'forks', 'forks')
      Timeseries(repo, 'linesOfCodeChanged', 'lines_changed')
      Timeseries(repo, 'maintainerResponseToMergeRequestDuration', 'pulls/maintainer_response_time')
      Timeseries(repo, 'newContributingGithubOrganizations', 'new_contributing_github_organizations')
      Timeseries(repo, 'openIssues', 'issues')
      Timeseries(repo, 'pullRequestComments', 'pulls/comments')
      Timeseries(repo, 'pullRequestsOpen', 'pulls')

      // RISK

      // VALUE

      // ACTIVITY
      Timeseries(repo, 'issueComments', 'issue_comments')
      Timeseries(repo, 'pullRequestsMadeClosed', 'pulls/made_closed')
      Timeseries(repo, 'watchers', 'watchers')

      // EXPERIMENTAL

      // Commit Related
      Timeseries(repo, 'commits100', 'commits100')
      Timeseries(repo, 'commitComments', 'commits/comments')
      Endpoint(repo, 'committerLocations', 'committer_locations')
      Timeseries(repo, 'totalCommitters', 'total_committers')

      // Issue Related
      Timeseries(repo, 'issueActivity', 'issues/activity')

      // Community / Contributions
      Endpoint(repo, 'communityAge', 'community_age')
      Timeseries(repo, 'communityEngagement', 'community_engagement')
      Endpoint(repo, 'contributors', 'contributors')
      Endpoint(repo, 'contributions', 'contributions')
      Endpoint(repo, 'projectAge', 'project_age')

      // Dependency Related
      Endpoint(repo, 'dependencies', 'dependencies')
      Endpoint(repo, 'dependencyStats', 'dependency_stats')
      Endpoint(repo, 'dependents', 'dependents')

      // Other
      Endpoint(repo, 'busFactor', 'bus_factor')
      Timeseries(repo, 'downloads', 'downloads')
      Timeseries(repo, 'fakes', 'fakes')
      Endpoint(repo, 'linkingWebsites', 'linking_websites')
      Timeseries(repo, 'majorTags', 'tags/major')
      Timeseries(repo, 'newWatchers', 'new_watchers')
      Timeseries(repo, 'tags', 'tags')
    }

    if (repo.gitURL) {
      // Other
      GitEndpoint(repo, 'changesByAuthor', 'changes_by_author')
      GitEndpoint(repo, 'linesOfCodeCommitCountsByCalendarYearGrouped', 'lines_of_code_commit_counts_by_calendar_year_grouped')
      GitEndpoint(repo, 'annualLinesOfCodeCountRankedByRepoInRepoGroup', 'annual_lines_of_code_count_ranked_by_repo_in_repo_group')
      GitEndpoint(repo, 'annualCommitCountRankedByRepoInRepoGroup', 'annual_commit_count_ranked_by_repo_in_repo_group')
      GitEndpoint(repo, 'annualLinesOfCodeCountRankedByNewRepoInRepoGroup', 'annual_lines_of_code_count_ranked_by_new_repo_in_repo_group')
      GitEndpoint(repo, 'annualCommitCountRankedByNewRepoInRepoGroup', 'annual_commit_count_ranked_by_new_repo_in_repo_group')
      GitEndpoint(repo, 'facadeProject', 'facade_project')
    }

    if (repo.repo_group_id && repo.repo_id) {
      addRepoMetric(repo, 'codeChanges', 'code-changes')
      addRepoMetric(repo, 'codeChangesLines', 'code-changes-lines')
      addRepoMetric(repo, 'issueNew', 'issues-new')
      addRepoMetric(repo, 'issuesClosed', 'issues-closed')
      addRepoMetric(repo, 'issueBacklog', 'issue-backlog')
      addRepoMetric(repo, 'pullRequestsMergeContributorNew', 'pull-requests-merge-contributor-new')
      addRepoMetric(repo, 'issuesFirstTimeOpened', 'issues-first-time-opened')
      addRepoMetric(repo, 'issuesFirstTimeClosed', 'issues-first-time-closed')
      addRepoMetric(repo, 'subProject', 'sub-projects')
      addRepoMetric(repo, 'contributors', 'contributors')
      addRepoMetric(repo, 'contributorsNew', 'contributors-new')
      addRepoMetric(repo, 'openIssuesCount', 'open-issues-count')
      addRepoMetric(repo, 'closedIssuesCount', 'closed-issues-count')
      addRepoMetric(repo, 'issuesOpenAge', 'issues-open-age')
      addRepoMetric(repo, 'issuesClosedResolutionDuration', 'issues-closed-resolution-duration')
      addRepoMetric(repo, 'issueActive', 'issues-active')
      addRepoMetric(repo, 'getIssues', 'get-issues')
    }

    if (repo.repo_group_id && repo.repo_id == null) {
      addRepoGroupMetric(repo, 'codeChanges', 'code-changes')
      addRepoGroupMetric(repo, 'codeChangesLines', 'code-changes-lines')
      addRepoGroupMetric(repo, 'issueNew', 'issues-new')
      addRepoGroupMetric(repo, 'issuesClosed', 'issues-closed')
      addRepoGroupMetric(repo, 'issueBacklog', 'issue-backlog')
      addRepoGroupMetric(repo, 'pullRequestsMergeContributorNew', 'pull-requests-merge-contributor-new')
      addRepoGroupMetric(repo, 'issuesFirstTimeOpened', 'issues-first-time-opened')
      addRepoGroupMetric(repo, 'issuesFirstTimeClosed', 'issues-first-time-closed')
      addRepoGroupMetric(repo, 'subProject', 'sub-projects')
      addRepoGroupMetric(repo, 'contributors', 'contributors')
      addRepoGroupMetric(repo, 'contributorsNew', 'contributors-new')
      addRepoGroupMetric(repo, 'openIssuesCount', 'open-issues-count')
      addRepoGroupMetric(repo, 'closedIssuesCount', 'closed-issues-count')
      addRepoGroupMetric(repo, 'issuesOpenAge', 'issues-open-age')
      addRepoGroupMetric(repo, 'issuesClosedResolutionDuration', 'issues-closed-resolution-duration')
      addRepoGroupMetric(repo, 'issueActive', 'issues-active')
      addRepoGroupMetric(repo, 'getIssues', 'get-issues')
    }

    return repo;
  }
}

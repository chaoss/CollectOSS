var $ = require('jquery')
var _ = require('lodash')

export default class AugurAPI {
  constructor (hostURL, version, autobatch) {
    this.__downloadedGitRepos = []

    this._version = version || '/api/unstable'
    this._host = hostURL || 'http://' + window.location.host
    this.__cache = {}
    this.__timeout = null
    this.__pending = {}

    this.getDownloadedGitRepos = this.__EndpointFactory('git/repos')
    this.openRequests = 0
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

  __endpointURL (endpoint) {
    return '' + this._host + this._version + '/' + endpoint
  }

  __URLFunctionFactory (url) {
    var self = this
    return function (params, callback) {
      this.openRequests++
      if (self.__cache[window.btoa(url)]) {
        if (self.__cache[window.btoa(url)].created_at > Date.now() - 1000 * 60) {
          return new Promise((resolve, reject) => {
            resolve(self.__cache[window.btoa(url)].data)
          })
        }
      }
      return $.get(url, params).then((data) => {
        this.openRequests--
        self.__cache[window.btoa(url)] = {
          created_at: Date.now(),
          data: data
        }
        return data
      })
    }
  }

  __EndpointFactory (endpoint) {
    return this.__URLFunctionFactory(this.__endpointURL(endpoint))
  }

  batch (endpoints) {
    let str = '[{"method": "GET", "path": "' + endpoints.join('"},{"method": "GET", "path": "') + '"}]'
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
    }).then((data) => {
      this.openRequests--
      // Save to cache
      this.__cache[window.btoa(url + endpoints.join(','))] = {
        created_at: Date.now(),
        data: data
      }
      return data
    })
  }

  batchMapped (repos, fields) {
    let endpoints = []
    let reverseMap = {}
    let processedData = {}
    repos.forEach((repo) => {
      Array.prototype.push.apply(endpoints, repo.batch(fields, true))
      _.assign(reverseMap, repo.__reverseEndpointMap)
      processedData[repo.toString()] = {}
    })
    return this.batch(endpoints).then((data) => {
      return new Promise((resolve, reject) => {
        if (Array.isArray(data)) {
          data.forEach(response => {
            if (response.status === 200) {
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = JSON.parse(response.response)
            } else {
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = null
            }
          })
          resolve(processedData)
        } else {
          reject(new Error('data-not-array'))
        }
      })
    })
  }

  Repo (repo) {
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
        repo.owner = splitURL[3]
        repo.name = splitURL[4].split('.')[0]
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
      this.getDownloadedGitRepos().then((data) => {
        let rs = false
        data.forEach((gitURL) => {
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

    var __Endpoint = (r, name, url) => {
      r[name] = this.__URLFunctionFactory(url)
      return r[name]
    }

    var Endpoint = (r, name, endpoint) => {
      var fullEndpoint = this._version + '/' + repo.owner + '/' + repo.name + '/' + endpoint
      var url = this._host + fullEndpoint
      r.__endpointMap[name] = fullEndpoint
      r.__reverseEndpointMap[fullEndpoint] = { name: name, owner: repo.toString() }
      return __Endpoint(r, name, url)
    }

    var Timeseries = (r, jsName, endpoint) => {
      let func = Endpoint(r, jsName, 'timeseries/' + endpoint)
      func.relativeTo = (baselineRepo, params, callback) => {
        var url = 'timeseries/' + endpoint + '/relative_to/' + baselineRepo.owner + '/' + baselineRepo.name
        return Endpoint(url)()
      }
      return func
    }

    var GitEndpoint = (r, jsName, endpoint) => {
      var url = this.__endpointURL('git/' + endpoint + '/' + r.gitURL)
      return __Endpoint(r, jsName, url)
    }

    repo.batch = (jsNameArray, noExecute) => {
      var routes = jsNameArray.map((e) => { return repo.__endpointMap[e] })
      if (noExecute) {
        return routes
      }
      return this.batch(routes).then((data) => {
        return new Promise((resolve, reject) => {
          if (Array.isArray(data)) {
            let mapped = {}
            data.forEach(response => {
              if (response.status === 200) {
                mapped[repo.__reverseEndpointMap[response.path].name] = JSON.parse(response.response)
              } else {
                mapped[repo.__reverseEndpointMap[response.path].name] = null
              }
            })
            resolve(mapped)
          } else {
            reject(new Error('data-not-array'))
          }
        })
      })
    }

    if (repo.owner && repo.name) {
      // DIVERSITY AND INCLUSION

      // GROWTH, MATURITY, AND DECLINE
      Timeseries(repo, 'issues', 'issues')
      Timeseries(repo, 'issuesClosed', 'issues/closed')
      Timeseries(repo, 'issuesResponseTime', 'issues/response_time')
      Timeseries(repo, 'commits', 'commits')
      Endpoint(repo, 'maintainerResponseTime', 'pull/maintainer_response_time')
      Timeseries(repo, 'forks', 'forks')
      Timeseries(repo, 'pulls', 'pulls')
      Timeseries(repo, 'pullReqComments', 'pulls/comments')
      Timeseries(repo, 'codeReviewIteration', 'code_review_iteration')
      Timeseries(repo, 'maintainerResponseTime', 'pulls/maintainer_response_time')
      Timeseries(repo, 'contributionAcceptance', 'contribution_acceptance')
      Timeseries(repo, 'newContributingGithubOrganizations', 'new_contributing_github_organizations')
      Endpoint(repo, 'contributingGithubOrganizations', 'contributing_github_organizations')
      // Timeseries(repo, 'codeReviews', 'code_reviews')

      // RISK
      Endpoint(repo, 'busFactor', 'bus_factor')

      // VALUE

      // ACTIVITY
      Timeseries(repo, 'issueComments', 'issue/comments')

      // EXPERIMENTAL

      // Commit Related
      Timeseries(repo, 'commits100', 'commits100')
      Timeseries(repo, 'commitComments', 'commits/comments')
      Timeseries(repo, 'totalCommitters', 'total_committers')
      Endpoint(repo, 'committerLocations', 'committer_locations')

      // Issue Related
      Timeseries(repo, 'issueActivity', 'issues/activity')

      // Pull Request Related
      Timeseries(repo, 'pullsAcceptanceRate', 'pulls/acceptance_rate')

      // Community / Contributions
      Endpoint(repo, 'watchers', 'watchers')
      Timeseries(repo, 'communityEngagement', 'community_engagement')
      Endpoint(repo, 'communityAge', 'community_age')
      Endpoint(repo, 'contributors', 'contributors')
      Endpoint(repo, 'contributions', 'contributions')

      // Dependency Related
      Endpoint(repo, 'dependencies', 'dependencies')
      Endpoint(repo, 'dependents', 'dependents')
      Endpoint(repo, 'dependencyStats', 'dependency_stats')

      // Other
      Timeseries(repo, 'linesChanged', 'lines_changed')
      Timeseries(repo, 'downloads', 'downloads')
      Timeseries(repo, 'fakes', 'fakes')
      Timeseries(repo, 'tags', 'tags')
      Endpoint(repo, 'linkingWebsites', 'linking_websites')
    }

    if (repo.gitURL) {
      // Other
      GitEndpoint(repo, 'linesChangedMinusWhitespace', 'lines_changed')
      GitEndpoint(repo, 'changesByAuthor', 'changes_by_author')
    }

    return repo
  }
}

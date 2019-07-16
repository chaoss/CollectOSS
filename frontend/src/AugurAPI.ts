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


  constructor(hostURL: string = 'http://localhost:5001', version: string = '/api/unstable', autobatch: any = null) {
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

  batchMapped(repos: Array<Repo>, fields: { forEach: (arg0: (field: any) => void) => void; }) {
    let endpoints: String[] | any[] = []
    let reverseMap: any = {}
    let processedData: any = {}
    repos.forEach((repo) => {
      // Array.prototype.push.apply(endpoints, repo.batch(fields, true))
      // _.assign(reverseMap, repo.__reverseEndpointMap)
      processedData[repo.toString()] = {}
      fields.forEach((field) => {
        // console.log("endpoint_map: ", field, repo, repo.__endpointMap[field])
        endpoints.push(repo.__endpointMap[field])
        reverseMap[repo.__endpointMap[field]] = repo.__reverseEndpointMap[repo.__endpointMap[field]]
      })
    })
    // console.log("before batch:", endpoints, reverseMap)
    return this.batch(endpoints).then((data: any) => {

      let newdat = new Promise((resolve, reject) => {
        if (Array.isArray(data)) {
          data.forEach((response) => {
            if (response.status === 200 && reverseMap[response.path]) {
              processedData[reverseMap[response.path].owner] = {}
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = []
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = JSON.parse(response.response)
              // console.log("pdata after response", processedData, typeof (reverseMap[response.path].owner), typeof (reverseMap[response.path].name), JSON.parse(response.response), response.response)
            } else if (reverseMap[response.path]) {
              // console.log('failed null')
              processedData[reverseMap[response.path].owner][reverseMap[response.path].name] = null
            }
          })
          // console.log(processedData)
          resolve(processedData)
        } else {
          reject(new Error('data-not-array'))
        }
      })
      // console.log(newdat, "newdata")
      return newdat
    })
  }

  Repo(repo: {githubURL?:string, gitURL?:string, repo_id?: number, repo_group_id?:number}){
      return new Repo(this, repo)
  }

  RepoGroup(rg: {rg_name:string, repo_group_id?:number}) {
    return new RepoGroup(this, rg)
  }
}

abstract class BaseRepo {
  private parent: AugurAPI
  public __endpointMap: {[key:string]:any}
  public __reverseEndpointMap: {[key:string]:{name:string, owner:string}}
  public _version: string
  public _host: string
  public gitURL?: string
  public githubURL?: string
  public name?:string
  public owner?:string
  public repo_group_id?:number
  public repo_id?:number
  __URLFunctionFactory: (url:string) => any
  [k: string]: any
  
  constructor(parent: AugurAPI){
    this._host = parent._host || 'http://' + window.location.host
    this._version = parent._version
    this.__URLFunctionFactory = parent.__URLFunctionFactory
    this.parent = parent
    this.__endpointMap = {}
    this.__reverseEndpointMap = {}
  }


  __Endpoint(name: string, url: string){
    this[name] = this.__URLFunctionFactory(url)
    return this[name]
  }

  __endpointURL(endpoint: string) {
    return '' + this._host + this._version + '/' + endpoint
  }

  Endpoint(name: string, endpoint: string) {
    var fullEndpoint = this._version + '/' + this.owner + '/' + this.name + '/' + endpoint
    var url = this._host + fullEndpoint
    this.__endpointMap[name] = fullEndpoint
    this.__reverseEndpointMap[fullEndpoint] = { name: name, owner: this.toString() }
    return this.__Endpoint(name, url)
  }

  Timeseries(jsName: string, endpoint: string){
    let func = this.Endpoint(jsName, 'timeseries/' + endpoint)
    // func.relativeTo = (baselineRepo:any, params:any, callback:any) => {
    //   var url = 'timeseries/' + endpoint + '/relative_to/' + baselineRepo.owner + '/' + baselineRepo.name
    //   return Endpoint(url)()
    // }
    return func
  }

  GitEndpoin(jsName: string, endpoint: string) {
    var url = this.__endpointURL('git/' + endpoint + '/?repo_url_base=' + window.btoa(this.gitURL||''))
    return this.__Endpoint(jsName, url)
  }

  addRepoMetric(jsName: string, endpoint: string){
    var url = this.__endpointURL('repo-groups/' + this.repo_group_id + '/repos/' + this.repo_id + '/' + endpoint)
    var fullEndpoint = this._version + '/repo-groups/' + this.repo_group_id + '/repos/' + this.repo_id + '/' + endpoint
    this.__endpointMap[jsName] = fullEndpoint
    this.__reverseEndpointMap[fullEndpoint] = { name: jsName, owner: this.toString() }
    return this.__Endpoint(jsName, url)
  }

  addRepoGroupMetric(jsName: string, endpoint: string){
    var url = this.__endpointURL('repo-groups/' + this.repo_group_id + '/' + endpoint)
    var fullEndpoint = this._version + '/' + 'repo-groups/' + this.repo_group_id + '/' + endpoint
    this.__endpointMap[jsName] = fullEndpoint
    this.__reverseEndpointMap[fullEndpoint] = { name: jsName, owner: this.toString() }
    return this.__Endpoint(jsName, url)
  }

  abstract toString():string

  batch(jsNameArray: Array<string>, noExecute: boolean) {
    var routes = jsNameArray.map((e: any) => { return this.__endpointMap[e] })
    if (noExecute) {
      return routes
    }
    return this.parent.batch(routes).then((data: any) => {
      return new Promise((resolve, reject) => {
        if (Array.isArray(data)) {
          let mapped: { [key: string]: any } = {}
          console.log()
          data.forEach(response => {
            if (response.status === 200) {
              mapped[this.__reverseEndpointMap[response.path].name] = JSON.parse(response.response)
              console.log('mapped:', mapped)
            } else {
              mapped[this.__reverseEndpointMap[response.path].name] = null
              console.log('mapped null:', mapped, this.__reverseEndpointMap[response.path])
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
}


class Repo extends BaseRepo{
  public rg_name?:string
  constructor(parent: AugurAPI, metadata:{githubURL?:string, gitURL?:string, repo_id?: number, repo_group_id?:number}){
    super(parent)
    this.gitURL = metadata.gitURL || undefined
    this.githubURL = metadata.githubURL || undefined
    this.repo_id = metadata.repo_id || undefined
    this.repo_group_id = metadata.repo_group_id || undefined
    this.getRepoNameAndID()
    this.initialLegacyMetric()
    this.initialMetric()
  }

  toString(){
    if (this.owner && this.name) {
      return this.owner + '/' + this.name
    } else {
      return this.gitURL||this.githubURL||this.repo_group_id +'/' + this.repo_id
    }
  }

  getRepoNameAndID(): void {
    if (this.githubURL) {
      let splitURL = this.githubURL.split('/')
      if (splitURL.length < 3) {
        this.owner = splitURL[0]
        this.name = splitURL[1]
      } else {
        this.owner = splitURL[3]
        this.name = splitURL[4]
      }
    }
    if (this.gitURL) {
      if (this.gitURL.includes('github.com')) {
        let splitURL = this.gitURL.split('/')
        this.owner = splitURL[1]
        this.name = splitURL[2].split('.')[0]
      } else {
        let splitURL = this.gitURL.split('/')
        this.owner = splitURL[0]
        this.name = splitURL[1]
      }
    }
    if (this.owner && this.name) {
      if (this.repo_id == null || this.repo_group_id == null) {
        let res: any = []
        $.ajax({
          type: "GET",
          url: this._version + '/repos/' + this.owner + '/' + this.name,
          async: false,
          success: function (data: any) {
            res = data;
          }
        })
        this.repo_id = res[0].repo_id
        this.repo_group_id = res[0].repo_group_id
        this.rg_name = res[0].rg_name
      }
    }
  } 
  initialLegacyMetric() {
    if (this.owner && this.name) {
      // DIVERSITY AND INCLUSION

      // GROWTH, MATURITY, AND DECLINE
      this.Timeseries('closedIssues', 'issues/closed')
      this.Timeseries('closedIssueResolutionDuration', 'issues/time_to_close')
      this.Timeseries( 'codeCommits', 'commits')
      // Timeseries('codeReviews', 'code_reviews')
      this.Timeseries('codeReviewIteration', 'code_review_iteration')
      this.Timeseries('contributionAcceptance', 'contribution_acceptance')
      this.Endpoint('contributingGithubOrganizations', 'contributing_github_organizations')
      this.Timeseries('firstResponseToIssueDuration', 'issues/response_time')
      this.Timeseries('forks', 'forks')
      this.Timeseries('linesOfCodeChanged', 'lines_changed')
      this.Timeseries('maintainerResponseToMergeRequestDuration', 'pulls/maintainer_response_time')
      this.Timeseries('newContributingGithubOrganizations', 'new_contributing_github_organizations')
      this.Timeseries('openIssues', 'issues')
      this.Timeseries('pullRequestComments', 'pulls/comments')
      this.Timeseries('pullRequestsOpen', 'pulls')

      // RISK

      // VALUE

      // ACTIVITY
      this.Timeseries('issueComments', 'issue_comments')
      this.Timeseries('pullRequestsMadeClosed', 'pulls/made_closed')
      this.Timeseries('watchers', 'watchers')

      // EXPERIMENTAL

      // Commit Related
      this.Timeseries('commits100', 'commits100')
      this.Timeseries('commitComments', 'commits/comments')
      this.Endpoint('committerLocations', 'committer_locations')
      this.Timeseries('totalCommitters', 'total_committers')

      // Issue Related
      this.Timeseries('issueActivity', 'issues/activity')

      // Community / Contributions
      this.Endpoint('communityAge', 'community_age')
      this.Timeseries('communityEngagement', 'community_engagement')
      this.Endpoint('contributors', 'contributors')
      this.Endpoint('contributions', 'contributions')
      this.Endpoint('projectAge', 'project_age')

      // Dependency Related
      this.Endpoint('dependencies', 'dependencies')
      this.Endpoint('dependencyStats', 'dependency_stats')
      this.Endpoint('dependents', 'dependents')

      // Other
      this.Endpoint('busFactor', 'bus_factor')
      this.Timeseries('downloads', 'downloads')
      this.Timeseries('fakes', 'fakes')
      this.Endpoint('linkingWebsites', 'linking_websites')
      this.Timeseries('majorTags', 'tags/major')
      this.Timeseries('newWatchers', 'new_watchers')
      this.Timeseries('tags', 'tags')
    }
  }
  initialMetric(){
    this.addRepoMetric('codeChanges', 'code-changes')
    this.addRepoMetric('codeChangesLines', 'code-changes-lines')
    this.addRepoMetric('issueNew', 'issues-new')
    this.addRepoMetric('issuesClosed', 'issues-closed')
    this.addRepoMetric('issueBacklog', 'issue-backlog')
    this.addRepoMetric('pullRequestsMergeContributorNew', 'pull-requests-merge-contributor-new')
    this.addRepoMetric('issuesFirstTimeOpened', 'issues-first-time-opened')
    this.addRepoMetric('issuesFirstTimeClosed', 'issues-first-time-closed')
    this.addRepoMetric('subProject', 'sub-projects')
    this.addRepoMetric('contributors', 'contributors')
    this.addRepoMetric('contributorsNew', 'contributors-new')
    this.addRepoMetric('openIssuesCount', 'open-issues-count')
    this.addRepoMetric('closedIssuesCount', 'closed-issues-count')
    this.addRepoMetric('issuesOpenAge', 'issues-open-age')
    this.addRepoMetric('issuesClosedResolutionDuration', 'issues-closed-resolution-duration')
    this.addRepoMetric('issueActive', 'issues-active')
    this.addRepoMetric('getIssues', 'get-issues')
  }
}


class RepoGroup extends BaseRepo {
  public rg_name?: string
  constructor(parent: AugurAPI, metadata:{rg_name:string, repo_group_id?:number}){
    super(parent)
    this.repo_group_id = metadata.repo_group_id || undefined
    this.rg_name = metadata.rg_name
    this.initialMetric()
  }

  toString(){
    return String(this.rg_name)
  }

  initialMetric(){
    if (this.repo_group_id) {
      this.addRepoGroupMetric('codeChanges', 'code-changes')
      this.addRepoGroupMetric('codeChangesLines', 'code-changes-lines')
      this.addRepoGroupMetric('issueNew', 'issues-new')
      this.addRepoGroupMetric('issuesClosed', 'issues-closed')
      this.addRepoGroupMetric('issueBacklog', 'issue-backlog')
      this.addRepoGroupMetric('pullRequestsMergeContributorNew','pull-requests-merge-contributor-new')
      this.addRepoGroupMetric('issuesFirstTimeOpened', 'issues-first-time-opened')
      this.addRepoGroupMetric('issuesFirstTimeClosed', 'issues-first-time-closed')
      this.addRepoGroupMetric('subProject', 'sub-projects')
      this.addRepoGroupMetric('contributors', 'contributors')
      this.addRepoGroupMetric('contributorsNew', 'contributors-new')
      this.addRepoGroupMetric('openIssuesCount', 'open-issues-count')
      this.addRepoGroupMetric('closedIssuesCount', 'closed-issues-count')
      this.addRepoGroupMetric('issuesOpenAge', 'issues-open-age')
      this.addRepoGroupMetric('issuesClosedResolutionDuration','issues-closed-resolution-duration')
      this.addRepoGroupMetric('issueActive', 'issues-active')
      this.addRepoGroupMetric('getIssues', 'get-issues')
    }
  }
}
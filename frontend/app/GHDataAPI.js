var $ = require('jquery')

export default class GHDataAPI {
  constructor(hostURL, version, autobatch) {
    this._version     = version || 'unstable'
    this._host        = hostURL || 'http://' + window.location.host + '/api/'
    this.__cache      = {}
    this.__timeout    = null
    this.__pending    = {}

    this.autobatch    = (typeof autobatch !== 'undefined') ? autobatch : true;
    this.openRequests = 0
  }

  __autobatcher(url, params, fireTimeout) {
    if (this.__timeout !== null && !fireTimeout) {
      this.__timeout = setTimeout(() => {
        __autobatch(undefined, undefined, true);
      })
    }
    return new Promise((resolve, reject) => {
      if (fireTimeout) {
        let batchURL = this._host + this._version + '/batch';
        let requestArray = [];
        Object.keys(this.__pending).forEach((key) => {
          requestArray.push({})
        })
        $.post(batchURL)
      }
    });
  }

  Repo(owner, repoName) {

    if (repoName) {
      var repo = {owner: owner, name: repoName}
    } else if (owner) {
      let splitURL = owner.split('/')
      if (splitURL.length < 3) {
        var repo = {owner: splitURL[0], name: splitURL[1]}
      } else {
        var repo = {owner: splitURL[3], name: splitURL[4]}
      }
    }

    repo.toString = () => { return repo.owner + '/' + repo.name }

    var Endpoint = (endpoint) => {
      this.openRequests++;
      var self = this;
      var url = this._host + this._version + '/' + repo.owner + '/' + repo.name + '/' + endpoint;
      return function (params, callback) {
        if (self.__cache[btoa(url)]) {
          if (self.__cache[btoa(url)].created_at > Date.now() - 1000 * 60) {
            return new Promise((resolve, reject) => {
              resolve(JSON.parse(self.__cache[btoa(url)].data))
            })
          }
        }
        if (this.autobatch) {
          return this.__autobatcher(url, params);
        }
        return $.get(url, params).then((data) => {
          this.openRequests--;
          self.__cache[btoa(url)] = {
            created_at: Date.now(),
            data: JSON.stringify(data)
          }
          if (typeof callback === 'function') {
            callback(data)
          }
          return new Promise((resolve, reject) => {
            resolve(data)
          })
        })
      }
    }

    var Timeseries = (endpoint) => {
      let func = Endpoint('timeseries/' + endpoint)
      func.relativeTo = (baselineRepo, params, callback) => {
        var url = 'timeseries/' + endpoint + '/relative_to/' + baselineRepo.owner + '/' + baselineRepo.name;
        return Endpoint(url)()
      }
      return func
    }

    repo.commits             = Timeseries('commits')
    repo.forks               = Timeseries('forks')
    repo.issues              = Timeseries('issues')
    repo.pulls               = Timeseries('pulls')
    repo.stars               = Timeseries('stargazers')
    repo.tags                = Timeseries('tags')
    repo.downloads           = Timeseries('downloads')
    repo.totalCommitters    = Timeseries('total_committers')
    repo.issueComments       = Timeseries('issue/comments')
    repo.commitComments      = Timeseries('commits/comments')
    repo.pullReqComments     = Timeseries('pulls/comments')
    repo.pullsAcceptanceRate = Timeseries('pulls/acceptance_rate')
    repo.issuesClosed        = Timeseries('issues/closed')
    repo.issuesResponseTime  = Timeseries('issues/response_time')


    repo.contributors        = Endpoint('contributors')
    repo.contributions       = Endpoint('contributions')
    repo.committerLocations  = Endpoint('committer_locations')
    repo.communityAge        = Endpoint('community_age')
    repo.linkingWebsites     = Endpoint('linking_websites')
    repo.busFactor           = Endpoint('bus_factor')
    repo.dependents          = Endpoint('dependents')
    repo.dependencies        = Endpoint('dependencies')
    repo.dependencyStats     = Endpoint('dependency_stats')
    repo.watchers            = Endpoint('watchers')

    return repo

  }
}

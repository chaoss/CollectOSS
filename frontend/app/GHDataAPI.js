var $ = require('jquery')

export default class GHDataAPI {
  constructor(hostURL, version, onStart, onUpdate, onDone) {
    this._version   = version || 'unstable'
    this._host      = hostURL || 'http://' + window.location.hostname + ':5000/'
    this.__cache    = {}
    this.__loading  = []
    this.__onStart  = onStart  || function () { console.log('Starting job...') }
    this.__onUpdate = onUpdate || function (a) { console.log('Loading ' + a[0]) }
    this.__onDone   = onDone   || function () { console.log('Finished job.') }
    this.ghtorrentRange = this.__Endpoint(this._host + this._version + '/ghtorrent_range')
  }

  __Endpoint(url) {
    var self = this;
    return function (params, callback) {
      if (!self.__loading.length) {
        self.__onStart()
      }
      self.__loading.push(url)
      if (self.__cache[btoa(url)]) {
        if (self.__cache[btoa(url)].created_at > Date.now() - 1000 * 60) {
          return new Promise((resolve, reject) => {
            resolve(JSON.parse(self.__cache[btoa(url)].data))
          })
        }
      }
      return new Promise((resolve, reject) => {
        $.get(url, params, (data, req) => {
          self.__onUpdate(self.__loading)
          self.__loading.splice(self.__loading.indexOf(url), 1)
          if (!self.__loading.length) {
            self.__onDone()
          }
          self.__cache[btoa(url)] = {
            created_at: Date.now(),
            data: JSON.stringify(data)
          }
          if (typeof callback === 'function') {
            callback(data)
          }
          if (data.length) {
            resolve(data)
          } else {
            reject(req)
          }
        }).fail((req) => {
          self.__loading.splice(self.__loading.indexOf(url), 1)
          if (!self.__loading.length) {
            self.__onDone()
          }
          reject(req)
        })
      })
    }
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

    let RepoEndpoint =  (endpoint) => {
      return this.__Endpoint(this._host + this._version + '/' + repo.owner + '/' + repo.name + '/' + endpoint);
    }

    let Timeseries = (endpoint) => {
      let func = RepoEndpoint('timeseries/' + endpoint)
      func.relativeTo = (baselineRepo, params, callback) => {
        var url = 'timeseries/' + endpoint + '/relative_to/' + baselineRepo.owner + '/' + baselineRepo.name;
        return RepoEndpoint(url)()
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
    repo.uniqueCommitters    = Timeseries('unique_committers')
    repo.pullsAcceptanceRate = Timeseries('pulls/acceptance_rate')

    repo.issuesResponseTime  = RepoEndpoint('issues/response_time')
    repo.contributors        = RepoEndpoint('contributors')
    repo.contributions       = RepoEndpoint('contributions')
    repo.committerLocations  = RepoEndpoint('committer_locations')
    repo.communityAge        = RepoEndpoint('community_age')
    repo.linkingWebsites     = RepoEndpoint('linking_websites')
    repo.busFactor           = RepoEndpoint('bus_factor')
    repo.dependents          = RepoEndpoint('dependents')
    repo.dependencies        = RepoEndpoint('dependencies')
    repo.dependencyStats     = RepoEndpoint('dependency_stats')

    repo.toString = () => {
      return repo.owner + '/' + repo.name
    }

    return repo

  }



}

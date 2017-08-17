var $ = require('jquery')

export default class GHDataAPI {
  constructor(hostURL, version) {
    this._version  = version || 'unstable'
    this._host     = hostURL || 'http://' + window.location.hostname + ':5000/'
    this.__cache   = {}
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
        return $.get(url, params, callback).then((data) => {
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

    repo.commits          = Timeseries('commits')
    repo.forks            = Timeseries('forks')
    repo.issues           = Timeseries('issues')
    repo.pulls            = Timeseries('pulls')
    repo.stars            = Timeseries('stargazers')
    repo.tags             = Timeseries('tags')
    repo.downloads        = Timeseries('downloads')
    repo.uniqueCommitters = Timeseries('unique_committers')


    repo.pullsAcceptanceRate = Endpoint('pulls/acceptance_rate')
    repo.issuesResponseTime  = Endpoint('issues/response_time')
    repo.contributors        = Endpoint('contributors')
    repo.contributions       = Endpoint('contributions')
    repo.committerLocations  = Endpoint('committer_locations')
    repo.communityAge        = Endpoint('community_age')
    repo.linkingWebsites     = Endpoint('linking_websites')
    repo.busFactor           = Endpoint('bus_factor')
    repo.dependents          = Endpoint('dependents')
    repo.dependencies        = Endpoint('dependencies')

    return repo

  }
}

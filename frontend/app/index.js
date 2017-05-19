window.riot = require('riot');

export function buildForm(owner, repo) {
  require('./components/healthreport')
  riot.mount('healthreport', {owner: owner, repo: repo})
}


export function start() {
  require('./components/githubform')
  riot.mount('githubform', {onsubmit: buildForm})
  //riot.mount('report', {owner: owner, repo: repo});
}
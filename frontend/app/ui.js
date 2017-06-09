import GHDataCharts from './GHDataCharts'
import GHDataAPI from './GHDataAPI'
var $ = require('jquery')


class GHDataDashboard {


  constructor(state) {
    this.state = state || {
      repo: {},
      comparedTo: {}
    }
    this.ghdata = new GHDataAPI()
  }



  addCard(title, repo, className) {
    let cardElement = document.createElement('section')
    if (className) {
      cardElement.className = className
    }
    let titleElement = document.createElement('h1')
    let repoElement = document.createElement('h2')
    titleElement.innerHTML = title
    repoElement.innerHTML = repo
    $('#cards').append(cardElement)
    $(cardElement).append(titleElement)
    $(cardElement).append(repoElement)
    return cardElement
  }

  renderComparisonForm() {
    var self = this
    if (this.comparisonCard) {
      this.comparisonCard.outerHTML = ''
    }
    this.comparisonCard = this.addCard(null, null, 'unmaterialized')
    $(this.comparisonCard).append($('#comparison-form-template')[0].innerHTML)
    $(this.comparisonCard).find('.search').on('keyup', function (e) {
      if (e.keyCode === 13) {
        self.renderComparisonRepo(null, self.ghdata.Repo(this.value))
      }
    })
  }

  renderBaseRepo(repo) {
    repo = repo || this.state.repo
    $('#main-repo-search').val(repo.owner + '/' + repo.name)
    var activityCard = this.addCard('Activity', '<strong>' + repo.owner + '/' + repo.name + '</strong>')
    activityCard.innerHTML += $('#base-template')[0].innerHTML
    $(activityCard).find('.linechart').each((index, element) => {
      let title = element.dataset.title || element.dataset.source[0].toUpperCase() + element.dataset.source.slice(1)
      repo[element.dataset.source]().then((data) => {
        console.log(data)
        GHDataCharts.LineChart(element, data, title)
      }, (error) => {
        GHDataCharts.NoChart(element, title)
      })
    })
    this.renderComparisonForm()
  }


  renderComparisonRepo(compareRepo, baseRepo) {
    compareRepo = compareRepo || this.state.repo
    var activityComparisonCard = this.addCard('Activity', '<strong>' + compareRepo.owner + '/' + compareRepo.name + '</strong> versus <strong>' + baseRepo.owner + '/' + baseRepo.name + '</strong>')
    activityComparisonCard.innerHTML += $('#base-template')[0].innerHTML
    $(activityComparisonCard).find('.linechart').each((index, element) => {
      let title = element.dataset.title || element.dataset.source[0].toUpperCase() + element.dataset.source.slice(1)
      compareRepo[element.dataset.source].relativeTo(baseRepo).then((data) => {
        console.log(data)
        GHDataCharts.ComparisonLineChart(element, data, title, baseRepo.owner + '/' + baseRepo.name)
      }, (error) => {
        GHDataCharts.NoChart(element, title)
      })
    })
    this.renderComparisonForm()
  }



  startSearch(url) {
    var $cards = $('#cards')
    $cards.html('')
    this.state.repo = this.ghdata.Repo(url)
    this.renderBaseRepo()
  }



}


$(document).ready(function () {

  $('.reposearch').on('keyup', function (e) {
    if (e.keyCode === 13) {
      window.dashboard = new GHDataDashboard()
      dashboard.startSearch(this.value)
    }
  })

})
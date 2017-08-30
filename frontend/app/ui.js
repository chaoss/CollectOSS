import GHDataCharts from './GHDataCharts'
import GHDataAPI from './GHDataAPI'
const queryString = require('query-string');

class GHDataDashboard {

  constructor(state) {
     this.EMPTY_STATE = {
      comparedTo: [],
      trailingAverage: 180,
      startDate: new Date('1 January 2005'),
      endDate: new Date()
    }
    this.STARTING_HTML = $('#cards')[0].innerHTML
    this.state = state || this.EMPTY_STATE
    this.ghdata = new GHDataAPI()
    if (/repo/.test(location.search) && !state) {
      console.log('State from URL')
      this.setStateFromURL()
    }
    window.addEventListener('popstate', (e) =>  {
      this.setStateFromURL()
    })
  }


  setStateFromURL() {
    let parsed = queryString.parse(location.search, {arrayFormat: 'bracket'})
    let state = {
      comparedTo: []
    }
    state.repo = this.ghdata.Repo(parsed.repo.replace(' ', '/'))
    if (parsed.comparedTo) {
      parsed.comparedTo.forEach((repo) => {
        state.comparedTo.push(this.ghdata.Repo(repo.replace(' ', '/')))
      })
    }
    this.state = state
    this.render()
  }


  pushState(state, title) {
    this.state = state || this.state
    title = title || this.state.repo.owner + '/' + this.state.repo.name
    let queryString = '?repo=' + this.state.repo.owner + '+' + this.state.repo.name
    this.state.comparedTo.forEach((repo) => {
      queryString += '&comparedTo[]=' + repo.owner + '+' + repo.name
    })
    history.pushState(null, title, queryString)
    document.title = title
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

  renderGraphs(element, repo) {
    $(element).find('.linechart').each((index, element) => {
      let title = element.dataset.title || element.dataset.source[0].toUpperCase() + element.dataset.source.slice(1)
      console.log(element.dataset.source)
      repo[element.dataset.source]().then((data) => {
        if (data && data.length) {
          $(element).find('cite').each( (i, e) => { $(e).show() } )
          GHDataCharts.LineChart(element, data, title, typeof element.dataset.rolling !== 'undefined', this.state.trailingAverage)
        } else {
          GHDataCharts.NoChart(element, title)
        }
      }, (error) => {
        GHDataCharts.NoChart(element, title)
      })
    })
  }


  renderBaseRepo(repo) {
    $('#control-container').removeClass('hidden')

    repo = repo || this.state.repo
    $('#main-repo-search').val(repo.owner + '/' + repo.name)

    var activityCard = this.addCard('Activity', '<strong>' + repo.owner + '/' + repo.name + '</strong>')
    activityCard.innerHTML += $('#base-template')[0].innerHTML
    this.renderGraphs(activityCard, repo)

    var ecosystemCard = this.addCard('Ecosystem', '<strong>' + repo.owner + '/' + repo.name + '</strong>')
    ecosystemCard.innerHTML += $('#ecosystem-template')[0].innerHTML
    this.renderGraphs(ecosystemCard, repo)
    repo.dependents().then((dependents) => {
      for (var i = 0; i < dependents.length && i < 10; i++) {
        $(ecosystemCard).find('#dependents').append(dependents[i].name + '<br>')
      }
    })
    repo.dependencies().then((dependencies) => {
      for (var i = 0; i < dependencies.dependencies.length && i < 10; i++) {
        $(ecosystemCard).find('#dependencies').append(dependencies.dependencies[i].name + '<br>')
      }
    })

    this.renderComparisonForm()
  }


  renderComparisonForm() {
    var self = this
    if (this.comparisonCard && this.comparisonCard.parentElement) {
      this.comparisonCard.outerHTML = ''
    }
    this.comparisonCard = this.addCard(null, null, 'unmaterialized')
    $(this.comparisonCard).append($('#comparison-form-template')[0].innerHTML)
    $(this.comparisonCard).find('.search').on('keyup', function (e) {
      if (e.keyCode === 13) {
        var comparedRepo = self.ghdata.Repo(this.value)
        self.state.comparedTo.push(comparedRepo)
        self.pushState()
        self.renderComparisonRepo(null, comparedRepo)
      }
    })
  }



  renderComparisonRepo(compareRepo, baseRepo) {
    compareRepo = compareRepo || this.state.repo
    var activityComparisonCard = this.addCard('Activity', '<strong>' + compareRepo.owner + '/' + compareRepo.name + '</strong> versus <strong>' + baseRepo.owner + '/' + baseRepo.name + '</strong>')
    activityComparisonCard.innerHTML += $('#base-template')[0].innerHTML
    $(activityComparisonCard).find('.linechart').each((index, element) => {
      let title = element.dataset.title || element.dataset.source[0].toUpperCase() + element.dataset.source.slice(1)
      compareRepo[element.dataset.source]().then((compare) => {
        let compareData = GHDataCharts.rollingAverage(GHDataCharts.convertToPercentages(compare), this.state.trailingAverage)
        baseRepo[element.dataset.source]().then((base) => {
          let baseData = GHDataCharts.rollingAverage(GHDataCharts.convertToPercentages(base), this.state.trailingAverage)
          let combinedData = GHDataCharts.combine(baseData, compareData)
          GHDataCharts.LineChart(element, combinedData, title, this.state.trailingAverage)
        }, (error) => {
          GHDataCharts.NoChart(element, title)
        })
      }, (error) => {
        GHDataCharts.NoChart(element, title)
      })
    })
    this.renderComparisonForm()
  }


  render(state) {
    state = state || this.state
    var $cards = $('#cards')
    $cards.html('')
    this.renderBaseRepo()
    state.comparedTo.forEach((repo) => {
      this.renderComparisonRepo(null, repo)
    })
  }


  startSearch(url) {
    this.state = this.EMPTY_STATE
    this.state.repo = this.ghdata.Repo(url)
    this.pushState()
    this.render()
  }


  reset() {
    var self = this
    $('#cards').html(this.STARTING_HTML).find('.reposearch').on('keyup', function (e) {
      if (e.keyCode === 13) {
        self.startSearch(this.value)
      }
    })
  }

}


$(document).ready(function () {

  var self = this;

  window.dashboard = new GHDataDashboard()

  $('.reposearch').on('keyup', function (e) {
    if (e.keyCode === 13) {
      dashboard.startSearch(this.value)
    }
  })

  var controls = $('#control-container')
  $(window).scroll(() => {    
   if ($(window).scrollTop() >= 219) {
      controls.addClass("fixed")
    } else {
      controls.removeClass("fixed")
    }
  });


  $('#averagetimespan').change(function (e) {
    dashboard.state.trailingAverage = this.value
  })

  $('#renderbutton').click(function (e) {
    dashboard.render()
  })

})

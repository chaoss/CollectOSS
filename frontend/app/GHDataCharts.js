import MG from 'metrics-graphics'
import * as d3 from 'd3'


export default class GHDataCharts {

  static convertDates (data) {
    if (Array.isArray(data[0])) {
      data.map((datum) => {
        return GHDataCharts.convertDates(datum)
      })
    } else {
      const EARLIEST = new Date('01-01-2005')
      data = data.map((d) => {
        d.date = new Date(d.date)
        return d
      }).filter((d) => {
        return d.date > EARLIEST
      })
    }
    return data
  }

  static rollingAverage(data, windowSizeInDays) {
    let windowMiliseconds = (windowSizeInDays * 24 /*hours*/ * 60 /*minutes*/ * 60 /*seconds*/ * 1000 /*miliseconds*/)
    let keys = Object.keys(data[0])
    let rolling = data.map((elem) => {
      let after = new Date(elem.date).getTime() - windowMiliseconds
      let before = new Date(elem.date).getTime()
      let average = {}
      let count = 0;
      data.forEach((toAverage) => {
        let testDate = new Date(toAverage.date).getTime()
        if (testDate <= before && testDate >= after) {
          count++;
          keys.forEach((prop) => {
            if (!isNaN(toAverage[prop] / 2.0) && average[prop] && prop !== 'date') {
              if (!average[prop]) {
                average[prop] = 0;
              }
              average[prop] += toAverage[prop]
            } else if (!isNaN(toAverage[prop] / 2.0) || prop === 'date') {
              average[prop] = toAverage[prop]
            }
          })
        }
      })
      for (var prop in average) {
        if (average.hasOwnProperty(prop) && prop !== 'date') {
          average[prop] = average[prop] / count;
          elem[prop + '_average'] = average[prop]
        }
      }
      return elem
    })
    return rolling
  }

  static convertToPercentages(data) {
    if (data && data[0]) {
      var keys = Object.keys(data[0])
    } else {
      return []
    }
    if (keys[1] !== 'date' && !isNaN(data[0][keys[1]] / 2.0)) {
      let baseline = (data[0][keys[1]] + data[1][keys[1]]) / 2
      if (isNaN(baseline)) {
        baseline = 1
      }
      data = data.map((datum) => {
        datum['value'] = datum[keys[1]] / baseline
        return datum
      })
    }
    return data
  }

  static combine() {
    return Array.from(arguments)
  }

  static ComparisonLineChart (selector, data, title, baseline) {
    GHDataCharts.convertDates(data)
    let keys = Object.keys(data[0]).filter((d) => { return /ratio/.test(d) })
    console.log(keys)
    return MG.data_graphic({
      title: title || 'Comparison',
      data: data,
      full_width: true,
      height: 200,
      baselines: [{value: 1, label: baseline || 'Other Repo'}],
      format: 'percentage',
      x_accessor: 'date',
      y_accessor: keys,
      target: selector
    })
  }

  static LineChart (selector, data, title, rollingAverage) {
    let data_graphic_config = {
      title: title || 'Activity',
      data: data,
      full_width: true,
      height: 200,
      x_accessor: 'date',
      target: selector
    }

    if (rollingAverage) {
      data_graphic_config.data = GHDataCharts.rollingAverage(data, 180)
      console.log(data_graphic_config.data)
      data_graphic_config.colors = ['#CCC', '#FF3647']
    }

    if (Array.isArray(data[0])) {
      data_graphic_config.legend = ['compared', 'base']
      data_graphic_config.colors = ['#FF3647', '#CCC']
    } else {
      data_graphic_config.y_accessor = Object.keys(data[0]).slice(1)
      data_graphic_config.legend = data_graphic_config.y_accessor
    }


    if (Object.keys(data_graphic_config.data[0]).slice(1).length > 1) {
    var legend = document.createElement('div')
      legend.style.position = 'relative'
      legend.style.margin = '0'
      legend.style.padding = '0'
      legend.style.height = '0'
      legend.style.top = '31px'
      legend.style.left = '55px'
      legend.style.fontSize = '14px'
      legend.style.fontWeight = 'bold'
      legend.style.opacity = '0.8'
      $(selector).append(legend)
      data_graphic_config.legend_target = legend
      $(selector).hover(() => {
        legend.style.display = 'none'
      }, () => {
        legend.style.display = 'block'
      })
    }

    GHDataCharts.convertDates(data)
    return MG.data_graphic(data_graphic_config)
  }

  static Timeline (selector, data, title) {
    var dataCleaned = []
    var legend = []
    for (var event in data) {
      if (data.hasOwnProperty(event)) {
        dataCleaned.push([{
          date: new Date(data[event]),
          value: 10
        }])
        legend.push(event)
      }
    }
    console.log(dataCleaned)
    return MG.data_graphic({
      title: title || 'Timeline',
      data: dataCleaned,
      full_width: true,
      height: 200,
      x_accessor: 'date',
      legend: legend,
      target: selector
    })
  }



  static NoChart (selector, title) {
    return MG.data_graphic({
      title: "Missing Data",
      error: 'Data unavaliable for ' + title,
      chart_type: 'missing-data',
      missing_text: title + ' could not be loaded',
      target: '#missing-data',
      full_width: true,
      height: 200
    })
  }

}

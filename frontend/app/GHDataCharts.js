window.$ = require('jquery')
window.jQuery = window.$ 

import MG from 'metrics-graphics'
import * as d3 from 'd3'

export default class GHDataCharts {

  static convertDates (data, earliest, latest) {
    earliest = earliest || new Date('01-01-2005')
    latest = latest || new Date()
    data.unshift({})
    if (Array.isArray(data[0])) {
      data = data.map((datum) => {
        return GHDataCharts.convertDates(datum)
      })
    } else {
      // Add 0 to beginning of data
      //if (new Date(data[0].date) > earliest) {
        var zero = {date: earliest}
        for (var prop in data[1]) {
          if (data[1].hasOwnProperty(prop) && prop !== 'date') {
            zero[prop] = 0;
          }
        }
        data.unshift(zero);
      //}
      data = data.map((d) => {
        d.date = new Date(d.date)
        return d
      }).filter((d) => {
        return earliest <= d.date && d.date <= latest
      })
    }
    return data
  }

  static convertKey (data, key) {
    if (Array.isArray(data[0])) {
      data = data.map((datum) => {
        return GHDataCharts.convertKey(datum, key)
      })
    } else {
      const EARLIEST = new Date('01-01-2005')
      data = data.map((d) => {
        d.value = d[key];
        return d;
      })
    }
    return data
  }

  static averageArray(ary) {
    return ary.reduce((a, e) => {return a + e}, 0) / (ary.length);
  }

  static standardDeviation(ary, key, mean) {
    let flat = ary.map((e) => {return e[key]})
    mean = mean || GHDataCharts.averageArray(flat)
    let distances = flat.map((e) => {
      return (e - mean) * (e - mean)
    })
    return Math.sqrt(GHDataCharts.averageArray(distances))
  }

  static describe(ary, key) {
    let flat = ary.map((e) => {return e[key]})
    let mean = GHDataCharts.averageArray(flat)
    let stddev = GHDataCharts.standardDeviation(ary, key, mean)
    let variance = stddev * stddev
    return {
      'mean': mean,
      'stddev': stddev,
      'variance': variance
    }
  }

  static rollingAverage(data, key, windowSizeInDays) {
    key = key || 'value'
    windowSizeInDays = windowSizeInDays || 180
    let rolling = [];
    let averageWindow = [];
    let i = 0;
    let lastFound = -1;

    let after = new Date()
    let before = new Date()

    for (let date = new Date(data[0].date); date <= data[data.length - 1].date; date.setDate(date.getDate() + 1)) {
      
      after.setDate(date.getDate() - windowSizeInDays)

      if (averageWindow.length < windowSizeInDays) {
        for (; i < data.length && averageWindow.length <= windowSizeInDays; i++) {
          if (lastFound > -1) {
            for (let iter = new Date(data[lastFound].date); iter <= data[i].date; iter.setDate(iter.getDate() + 1)) {
              averageWindow.push( (data[i][key] + data[lastFound][key]) / 2 )
            }
          }
          lastFound = i
        }
      }

      let average = {date: new Date(date)}
      average[key] = GHDataCharts.averageArray(averageWindow.slice(0, windowSizeInDays));
      averageWindow.shift()
      rolling.push(average);
    }
    return rolling
  }

  static convertToPercentages(data, key, baseline) {
    if (!data) {
      return []
    }
    baseline = baseline || GHDataCharts.averageArray( data.map((e) => {return e[key]}) )
    data = data.map((datum) => {
      datum['value'] = (datum[key] / baseline)
      return datum
    })
    return data
  }

  static makeRelative(baseData, compareData, config) {

    config.byDate = (config.byDate != undefined)
    config.earliest = config.earliest || new Date('01-01-2005')
    config.latest = config.latest || new Date()
    config.period = config.period || 180

    let iter = {
      base: 0,
      compare: 0
    }
    let data = {}

    data['base'] = GHDataCharts.rollingAverage(
                     GHDataCharts.convertDates(
                       GHDataCharts.convertKey(
                         baseData, 
                         Object.keys(baseData[0])[1]
                     ), config.earliest, config.latest
                   ), undefined, config.period) 

    data['compare'] = GHDataCharts.rollingAverage(
                        GHDataCharts.convertDates(
                          GHDataCharts.convertKey(
                            compareData, 
                            Object.keys(compareData[0])[1]
                        ), config.earliest, config.latest
                      ), undefined, config.period) 

    let smaller = (data['base'][0].date < data['compare'][0].date) ? 'base' : 'compare'
    let larger  = (data['base'][0].date < data['compare'][0].date) ? 'compare' : 'base'
    let result  = []

    if (config.byDate) {
      for (; iter[smaller] < data[smaller].length; iter[smaller]++) {
        if (data['base'].date == data['compare'].date) {
          break
        }
      }
    }

    while (iter['base'] < data['base'].length && iter['compare'] < data['compare'].length) {
      let toPush = {
        value: data['compare'][iter.compare].value / data['base'][iter.base].value,
      }
      if (config.byDate) {
        toPush.date = data['base'][iter.base].date
      } else {
        toPush.x = iter.base
      }
      result.push(toPush)
      iter['base']++
      iter['compare']++
    }

    return result
  }

  static zscores(data, key) {
    key = key || 'value'
    let stats = GHDataCharts.describe(data, key)
    return data.map((e) => {
      let newObj = {}
      if (e.date) {
        newObj.date = new Date(e.date)
      }
      let zscore = ((e[key] - stats['mean']) / stats['stddev'])
      newObj.value = zscore
      return newObj
    })
  }

  static combine() {
    return Array.from(arguments)
  }

  static ComparisonLineChart (selector, baseData, compareData, config) {

    config.title = config.title || 'Comparison'
    config.byDate = (config.byDate != undefined)
    config.earliest = config.earliest || new Date('01-01-2005')
    config.latest = config.latest || new Date()
    config.baseline = config.baseline || 'Compared Repo'
    config.legend = config.legend || 'Base Repo'
    config.full_width = true
    config.height = 200
    config.colors = ['#FF3647']
    config.area = false
    config.baselines = [{value: 1, label: config.baseline}]
    config.format = 'percentage'
    config.x_accessor = config.byDate ? 'date' : 'x'
    config.target = selector

    config.data = GHDataCharts.makeRelative(baseData, compareData, config)

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
    $(selector).hover(() => {
      legend.style.display = 'none'
    }, () => {
      legend.style.display = 'block'
    })

    config.legend = config.legend
    config.legend_target = legend

    $(selector).css({"background-image": "none"})

    return MG.data_graphic(config)
  }

  static LineChart (selector, data, config) {

    config.title = config.title || 'Activity'
    config.period = config.period || 180
    config.earliest = config.earliest || new Date('01-01-2005')
    config.latest = config.latest || new Date()
    config.data = data,
    config.full_width = true,
    config.height = 200,
    config.x_accessor = 'date',
    config.target = selector

    if (config.percentage) {
      config.format = 'percentage';
    }

    data = GHDataCharts.convertDates(data, config.earliest, config.latest)

    if (config.rollingAverage) {
      config.legend = config.legend || [config.title.toLowerCase(), config.period + ' day average']
      let rolling = GHDataCharts.rollingAverage(data, Object.keys(data[0])[1], config.period)
      config.data = GHDataCharts.convertKey(GHDataCharts.combine(data, rolling), Object.keys(data[0])[1])
      config.colors = config.colors ||['#CCC', '#FF3647']
      config.y_accessor = 'value';
    }

    if (Array.isArray(config.data[0])) {
      config.legend = config.legend || ['compared', 'base']
      config.colors = config.colors || ['#FF3647', '#999']
      config.y_accessor = config.y_accessor || 'value'
    } else {
      config.y_accessor = Object.keys(data[0]).slice(1)
      config.legend = config.y_accessor
    }


    if (Object.keys(config.data[0]).slice(1).length > 1) {
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
      config.legend_target = legend
      $(selector).hover(() => {
        legend.style.display = 'none'
      }, () => {
        legend.style.display = 'block'
      })
    }
    
    $(selector).css({"background-image": "none"})
    let chart = MG.data_graphic(config)
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
    $(selector).css({"background-image": "none"})
    return MG.data_graphic({
      error: 'Data unavaliable for ' + title,
      chart_type: 'missing-data',
      missing_text: '⚠ Data Missing for ' + title,
      target: selector,
      full_width: true,
      height: 200
    })
  }

}

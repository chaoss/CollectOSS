window.$ = require('jquery')
window.jQuery = window.$ 

import MG from 'metrics-graphics'
import * as d3 from 'd3'

export default class GHDataCharts {

  static convertDates (data, earliest, latest) {
    earliest = earliest || new Date('01-01-2005')
    latest = latest || new Date()
    if (Array.isArray(data[0])) {
      data = data.map((datum) => {
        return GHDataCharts.convertDates(datum)
      })
    } else {
      
      data = data.map((d) => {
        d.date = new Date(d.date)
        return d
      }).filter((d) => {
        return earliest < d.date && d.date < latest
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
    ary.push(0)
    return ary.reduce((a, e) => {return a + e}) / (ary.length - 1);
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
    console.log(data)
    if (!data) {
      return []
    }
    baseline = baseline || GHDataCharts.averageArray( data.map((e) => {return e[key]}) )
    console.log(baseline)
    data = data.map((datum) => {
      datum['value'] = (datum[key] / baseline)
      return datum
    })
    return data
  }

  static combine() {
    return Array.from(arguments)
  }

  static ComparisonLineChart (selector, data, title, baseline, earliest, latest) {
    data = GHDataCharts.convertDates(data, earliest, latest)
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

  static LineChart (selector, data, config) {

    config.title = config.title || 'Activity'
    config.rollingAverage = (config.rollingAverage == true)
    config.period = config.period || 180
    config.earliest = config.earliest || new Date('01-01-2005')
    config.latest = config.latest || new Date()
    config.percentage = (config.percentage == true)


    let data_graphic_config = {
      title:  config.title,
      data: data,
      full_width: true,
      height: 200,
      x_accessor: 'date',
      legend: config.legend,
      colors: config.colors,
      target: selector
    }

    if (config.percentage) {
      data_graphic_config.format = 'percentage';
    }

    data = GHDataCharts.convertDates(data, config.earliest, config.latest)

    if (config.rollingAverage) {
      data_graphic_config.legend = data_graphic_config.legend || [config.title.toLowerCase(), config.period + ' day average']
      let rolling = GHDataCharts.rollingAverage(data, Object.keys(data[0])[1], config.period)
      data_graphic_config.data = GHDataCharts.convertKey(GHDataCharts.combine(data, rolling), Object.keys(data[0])[1])
      data_graphic_config.colors = data_graphic_config.colors ||['#CCC', '#FF3647']
      data_graphic_config.y_accessor = 'value';
    }

    if (Array.isArray(data_graphic_config.data[0])) {
      data_graphic_config.legend = data_graphic_config.legend || ['compared', 'base']
      data_graphic_config.colors = data_graphic_config.colors || ['#FF3647', '#999']
      data_graphic_config.y_accessor = data_graphic_config.y_accessor || 'value'
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
    
    let chart = MG.data_graphic(data_graphic_config)
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

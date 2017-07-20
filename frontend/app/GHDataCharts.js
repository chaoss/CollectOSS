import MG from 'metrics-graphics'
import * as d3 from 'd3'


export default class GHDataCharts {

  static convertDates (data) {
    data = data.map((d) => {
      d.date = new Date(d.date)
      return d
    })
    return data
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

  static LineChart (selector, data, title) {
    GHDataCharts.convertDates(data)
    return MG.data_graphic({
      title: title || 'Activity',
      data: data,
      full_width: true,
      height: 200,
      x_accessor: 'date',
      y_accessor: Object.keys(data[0]).slice(1),
      target: selector,
      legend: Object.keys(data[0]).slice(1)
    })
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

export default class AugurStats {
  static convertDates (data, earliest, latest, key) {
    key = key || 'date'
    earliest = earliest || new Date('01-01-2005')
    latest = latest || new Date()
    if (Array.isArray(data[0])) {
      data = data.map((datum) => {
        return AugurStats.convertDates(datum)
      })
    } else {
      data = data.map((d) => {
        d.date = new Date(d[key])
        return d
      }).filter((d) => {
        return earliest < d.date && d.date < latest
      }).sort((a, b) => {
        return a.date - b.date
      })
    }
    return data
  }

  static convertKey (data, key) {
    if (Array.isArray(data[0])) {
      data = data.map((datum) => {
        return AugurStats.convertKey(datum, key)
      })
    } else if (key.length > 1){
      return data.map((d) => {
        return {
          date: d.date,
          value: d[key[0]],
          field: d[key[1]]
        }
      })
    }
    else{
      return data.map((d) => {
        return {
          date: d.date,
          value: d[key]
        }
      })
    }
    return data
  }

  static convertComparedKey (data, key) {
    if (Array.isArray(data[0])) {
      data = data.map((datum) => {
        return AugurStats.convertKey(datum, key)
      })
    } else {
      return data.map((d) => {
        return {
          date: d.date,
          comparedValue: d[key]
        }
      })
    }
    return data
  }

  static averageArray (ary) {
    let len = ary.length
    let sum = ary.reduce((a, e) => {
      if (isFinite(e)) {
        return a + e
      } else {
        len--
        return a
      }
    }, 0)
    return (sum / len) || 0
  }

  static aboveAverage (data, key) {
    let flat = data.map((e) => { return e[key] })
    let mean = AugurStats.averageArray(flat)
    return data.filter((e) => {
      return e[key] > mean
    })
  }

  static standardDeviationLines (data, key, extension, mean) {
    let flat = data.map((e) => { return e[key] })
    mean = mean || AugurStats.averageArray(flat)
    let distances = flat.map((e) => {
      return (e - mean) * (e - mean)
    })
    return data.map((e) => {
      let newObj = {}
      if (e.date) {
        newObj.date = new Date(e.date)
        newObj[key] = e[key]
      }
      newObj['upper' + extension] = e[key] + Math.sqrt(AugurStats.averageArray(distances))
      newObj['lower' + extension] = e[key] - Math.sqrt(AugurStats.averageArray(distances))
      return newObj
    })
  }

  static standardDeviation (data, key, mean) {
    let flat = data.map((e) => { return e[key] })
    mean = mean || AugurStats.averageArray(flat)
    let distances = flat.map((e) => {
      return (e - mean) * (e - mean)
    })
    return Math.sqrt(AugurStats.averageArray(distances))
  }

  static describe (ary, key) {
    let flat = AugurStats.flatten(ary, key)
    let mean = AugurStats.averageArray(flat)
    let stddev = AugurStats.standardDeviation(ary, key, mean)
    let variance = stddev * stddev
    return {
      'mean': mean,
      'stddev': stddev,
      'variance': variance
    }
  }

  static flatten (array, key) {
    return array.map((e) => { return e[key] })
  }

  static rollingAverage (data, key, windowSizeInDays) {
    //key = key || 'value'
    let period = (windowSizeInDays / 2)
    data = data.filter(datum => {
      return isFinite(datum[key])
    })
    return AugurStats.dateAggregate(data, period, period, (period / 2), (filteredData, date) => {
      let flat = AugurStats.flatten(filteredData, key)
      let datum = { date: date }
      datum[key + "Rolling"] = Math.round(AugurStats.averageArray(flat)*100)/100
      return datum
    })
  }

  static dateAggregate (data, daysBefore, daysAfter, interval, func) {
    daysBefore = daysBefore || 30
    interval = interval || ((daysAfter + daysBefore) / 4)
    let rolling = []
    let averageWindow = []
    let i = 0

    let earliest = new Date()
    let latest = new Date()

    for (let date = new Date(data[0].date); date <= data[data.length - 1].date; date.setDate(date.getDate() + interval)) {
      earliest = (new Date(date)).setDate(date.getDate() - daysBefore)
      latest = (new Date(date)).setDate(date.getDate() + daysAfter)
      averageWindow = data.filter((d) => {
        return (earliest <= d.date) && (d.date <= latest)
      })
      rolling.push(func(averageWindow, new Date(date), i))
      i++
    }
    return rolling
  }

  static convertToPercentages (data, key, baseline) {
    if (!data) {
      return []
    }
    baseline = baseline || AugurStats.averageArray(data.map((e) => { return e[key] }))
    data = data.map((datum) => {
      datum['value'] = (datum[key] / baseline)
      return datum
    })
    return data
  }

  static makeRelative (baseData, compareData, key, config) {
    config.byDate = (config.byDate === true)
    config.earliest = config.earliest || new Date('01-01-2005')
    config.latest = config.latest || new Date()
    config.period = config.period || 180
    key = key || Object.keys(baseData[0])[1]

    let iter = {
      base: 0,
      compare: 0
    }
    let data = {}

    data['base'] = AugurStats.rollingAverage(
      AugurStats.convertDates(
        AugurStats.convertKey(
          baseData,
          key
        ), config.earliest, config.latest
      ), undefined, config.period)

    data['compare'] = AugurStats.rollingAverage(
      AugurStats.convertDates(
        AugurStats.convertKey(
          compareData,
          key
        ), config.earliest, config.latest
      ), undefined, config.period)

    let result = []

    while (iter['base'] < data['base'].length && iter['compare'] < data['compare'].length) {
      let toPush = {
        value: data['compare'][iter.compare].value / data['base'][iter.base].value
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

    console.log('relative', result)
    return result
  }

  static zscores (data, key) {
    // key = key || 'value'
    let stats = AugurStats.describe(data, key)
    return data.map((e) => {
      let newObj = {}
      if (e.date) {
        newObj.date = new Date(e.date)
      }
      let zscore = ((e[key] - stats['mean']) / stats['stddev'])
      newObj[key] = zscore
      return newObj
    })
  }

  static combine () {
    return Array.from(arguments)
  }
}

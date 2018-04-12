export default class AugurStats {

  static convertDates (data, earliest, latest) {
    earliest = earliest || new Date('01-01-2005')
    latest = latest || new Date()
    if (Array.isArray(data[0])) {
      data = data.map((datum) => {
        return AugurStats.convertDates(datum)
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
        return AugurStats.convertKey(datum, key)
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

  static aboveAverage(data, key) {
    let flat = data.map((e) => {return e[key]})
    let mean = AugurStats.averageArray(flat)
    return data.filter((e) => {
      return e[key] > mean
    })
  }

  static standardDeviation(ary, key, mean) {
    let flat = ary.map((e) => {return e[key]})
    mean = mean || AugurStats.averageArray(flat)
    let distances = flat.map((e) => {
      return (e - mean) * (e - mean)
    })
    return Math.sqrt(AugurStats.averageArray(distances))
  }

  static describe(ary, key) {
    let flat = ary.map((e) => {return e[key]})
    let mean = AugurStats.averageArray(flat)
    let stddev = AugurStats.standardDeviation(ary, key, mean)
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
      average[key] = AugurStats.averageArray(averageWindow.slice(0, windowSizeInDays));
      averageWindow.shift()
      rolling.push(average);
    }
    return rolling
  }

  static convertToPercentages(data, key, baseline) {
    if (!data) {
      return []
    }
    baseline = baseline || AugurStats.averageArray( data.map((e) => {return e[key]}) )
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

    data['base'] = AugurStats.rollingAverage(
                     AugurStats.convertDates(
                       AugurStats.convertKey(
                         baseData, 
                         Object.keys(baseData[0])[1]
                     ), config.earliest, config.latest
                   ), undefined, config.period) 

    data['compare'] = AugurStats.rollingAverage(
                        AugurStats.convertDates(
                          AugurStats.convertKey(
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

    console.log('relative', result)
    return result
  }

  static zscores(data, key) {
    key = key || 'value'
    let stats = AugurStats.describe(data, key)
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

}
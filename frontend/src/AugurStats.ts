// #SPDX-License-Identifier: MIT
/* tslint:disable */
export default class AugurStats {
    static convertDates (data:any, earliest: Date = new Date('01-01-2005'), latest: Date = new Date(), key: string = 'date') {
      key = key || 'date'
      earliest = earliest || new Date('01-01-2005')
      latest = latest || new Date()
      if (Array.isArray(data[0])) {
        data = data.map((datum: any) => {
          return AugurStats.convertDates(datum)
        })
      } else {
        data = data.map((d:any) => {
          d.date = new Date(d[key])
          return d
        }).filter((d: any) => {
          return earliest < d.date && d.date < latest
        }).sort((a:any, b:any) => {
          return a.date - b.date
        })
      }
      return data
    }
  
    static convertKey (data:any, key:any, newName:string = "value") {
      newName = newName || "value"
      if (Array.isArray(data[0])) {
        data = data.map((datum:any) => {
          return AugurStats.convertKey(datum, key)
        })
      } else if (key.length > 1){
        return data.map((d:any) => {
          let obj:any = {
            date: d.date,
            field: d[key[1]]
          }
          obj[newName] = d[key]
          return obj
        })
      }
      else{
        return data.map((d:any) => {
          let obj:any = {
            date: d.date,
          }
          obj[newName] = d[key] || 0
          return obj
        })
      }
      return data
    }
  
    static convertComparedKey (data:any, key:string) {
      if (Array.isArray(data[0])) {
        data = data.map((datum:any) => {
          return AugurStats.convertKey(datum, key)
        })
      } else {
        return data.map((d:any) => {
          return {
            date: d.date,
            comparedValue: d[key]
          }
        })
      }
      return data
    }
  
    static averageArray (ary:any) {
      let len = ary.length
      let sum = ary.reduce((a:any, e:any) => {
        if (isFinite(e)) {
          return a + e
        } else {
          len--
          return a
        }
      }, 0)
      return (sum / len) || 0
    }
  
    static aboveAverage (data: any, key: string) {
      let flat = data.map((e:any) => { return e[key] })
      let mean = AugurStats.averageArray(flat)
      return data.filter((e:any) => {
        return e[key] > mean
      })
    }
  
    static standardDeviationLines (data:any, key:string, addon:any, mean: number) {
      let flat = data.map((e:any) => { return e[key] })
      console.log(addon.replace(/\//g,''))
      addon = addon.replace(/\//g,'')
      console.log(addon.replace(/\./g,''))
      addon = addon.replace(/\./g,'')
  
      let extension = addon
      console.log(extension)
      mean = mean || AugurStats.averageArray(flat)
      let distances = flat.map((e:number) => {
        return (e - mean) * (e - mean)
      })
      return data.map((e:any) => {
        let newObj: any = {}
        if (e.date) {
          newObj.date = new Date(e.date)
          newObj[key + extension] = e[key]
        }
        newObj['date' + addon] = newObj.date
        // newObj['upper' + extension] = e[key] + Math.sqrt(AugurStats.averageArray(distances))
        // newObj['lower' + extension] = e[key] - Math.sqrt(AugurStats.averageArray(distances))
        return newObj
      })
    }
  
    static standardDeviation (data:any, key:string, mean:number) {
      let flat = data.map((e:any) => { return (e[key] ? e[key] : 0) })
  
      mean = mean || AugurStats.averageArray(flat)
      let distances = flat.map((e:number) => {
        return (e - mean) * (e - mean)
      })
      return Math.sqrt(AugurStats.averageArray(distances))
    }
  
    static describe (ary:any, key:string) {
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
  
    static flatten (array:any, key:string) {
      return array.map((e:any) => { return e[key] })
    }
  
    static rollingAverage (data:any, key:string = 'value', windowSizeInDays: number) {
      key = key || 'value'
      let period = (windowSizeInDays / 2)
      data = data.filter((datum:any) => {
        return isFinite(datum[key])
      })
      // if (data[0].date != startDate) {
      //   let test = startDate
      //   while (data[0].date - test > period) {
      //     test += period
      //   }
      //   var offset = data[0].date - test
      // }
      // let before = offset ? offset : period
      // let after = offset ? period - offset : period
      return AugurStats.dateAggregate(data, period, period, (period / 2), (filteredData: any, date: any) => {
        let flat = AugurStats.flatten(filteredData, key)
        let datum: any = { date: date }
        let newKey = (key + "Rolling")
        datum[newKey] = Math.round(AugurStats.averageArray(flat)*100)/100
        return datum
      })
    }
  
    static dateAggregate (data:any, daysBefore:number=30, daysAfter:number, interval:number=((daysAfter + daysBefore) / 4), func:any) {
      daysBefore = daysBefore || 30
      interval = interval || ((daysAfter + daysBefore) / 4)
      let rolling = []
      let averageWindow = []
      let i = 0
  
      let earliest:Date = new Date()
      let latest:Date = new Date()
  
      for (let date = new Date(data[0].date); date <= data[data.length - 1].date; date.setDate(date.getDate() + interval)) {
        earliest = new Date((new Date(date)).setDate(date.getDate() - daysBefore))
        latest = new Date((new Date(date)).setDate(date.getDate() + daysAfter))
        averageWindow = data.filter((d:{date: Date}) => {
          return (earliest <= d.date) && (d.date <= latest)
        })
        rolling.push(func(averageWindow, new Date(date), i))
        i++
      }
      return rolling
    }
  
    static alignDates (data:any, baseDate:Date, windowSizeInDays:number) {
      //key = key || 'value'
      let period = (windowSizeInDays / 2)
      data.unshift({date: baseDate, value: null})
      return data
    }
  
    static convertToPercentages (data:any, key:string, baseline:any=null) {
      if (!data) {
        return []
      }
      baseline = baseline || AugurStats.averageArray(data.map((e:any) => { return e[key] }))
      data = data.map((datum:any) => {
        datum['value'] = (datum[key] / baseline)
        return datum
      })
      return data
    }
  
    static makeRelative (baseData:any, compareData:any, key:string, config:any) {
      config.byDate = (config.byDate === true)
      config.earliest = config.earliest || new Date('01-01-2005')
      config.latest = config.latest || new Date()
      config.period = config.period || 180
      key = key || Object.keys(baseData[0])[1]
  
      let iter = {
        base: 0,
        compare: 0
      }
      let data:{[key:string]:any} = {}
  
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
        let toPush:any = {
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
      return result
    }
  
    static zscores (data:any, key:string) {
      // key = key || 'value'
      let stats = AugurStats.describe(data, key)
      return data.map((e:any) => {
        let newObj:any = {}
        // if (e.date) {
          newObj.date = new Date(e.date)
        // } else {
        //   newObj.date = 
        // }
        let zscore = stats['stddev'] == 0 ? 0 : ((e[key] - stats['mean']) / stats['stddev'])
        newObj[key] = zscore
        return newObj
      })
    }
  
    static combine () {
      return Array.from(arguments)
    }
  }
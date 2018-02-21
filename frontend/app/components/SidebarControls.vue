<template>
<div class="row" id="controls">
  <div class="col col-12">
    <div class="form">
      <h4>Base Repository</h4>
      <div class="form-item">
        <label>Start Date
          <div class="row gutters">
            <div class="col col-6">
              <div class="form-item">
                <select id="start-month" @change=onStartDateChange>
                  <option v-for="month in months" v-bind:value="month.value" v-bind:selected="month.value == 0">{{ month.name }}</option>
                </select>
                <div class="desc">Month</div>
              </div>
            </div>
            <div class="col col-6">
              <div class="form-item">
                <select id="start-year" @change=onStartDateChange>
                  <option v-for="year in years" v-bind:value="year" v-bind:selected="year == 2005">{{ year }}</option>
                </select>
                <div class="desc">Year</div>
              </div>
            </div>
          </div>
        </label>
      </div>
      <div class="form-item">
        <label>End Date
          <div class="row gutters">
            <div class="col col-6">
              <div class="form-item">
                <select id="end-month" @change=onEndDateChange>
                  <option v-for="month in months" v-bind:value="month.value" v-bind:selected="month.value == thisMonth">{{ month.name }}</option>
                </select>
                <div class="desc">Month</div>
              </div>
            </div>
            <div class="col col-6">
              <div class="form-item">
                <select id="end-year" @change=onEndDateChange>
                  <option v-for="year in years" v-bind:value="year" v-bind:selected="year == thisYear">{{ year }}</option>
                </select>
                <div class="desc">Year</div>
              </div>
            </div>
          </div>
        </label>
      </div>
      <div class="form-item">
        <label>Trailing Average</label>
        <div class="append">
          <input type="number" min="2" id="averagetimespan" value="180" @change="onTrailingAverageChange"><span>days</span>
        </div>
      </div>
      <h4>Comparisons</h4>
      <div class="form-item form-checkboxes">
        <label class="checkbox"><input name="comparebaseline" value="each" checked type="radio" @change="onCompareChange">Z-score trailing average</label>
        <label class="checkbox"><input name="comparebaseline" value="percentage" type="radio" @change="onCompareChange">100% is the compared project</label>
      </div>
    </div>
  </div>
</div>
</template>

<script>
  module.exports = {
    methods: {
      onStartDateChange (e) {
        var date = Date.parse((document.getElementById("start-month").value + "/01/" + document.getElementById("start-year").value))
        if (this.startDateTimeout) {
          clearTimeout(this.startDateTimeout)
        }
        this.startDateTimeout = setTimeout(() => {
          this.$store.commit('setDates', {
            startDate: date
          })
        }, 500);
      },
      onEndDateChange (e) {
        var date = Date.parse((document.getElementById("end-month").value + "/01/" + document.getElementById("end-year").value))
        if (this.endDateTimeout) {
          clearTimeout(this.endDateTimeout)
          delete this.endDateTimeout
        }
        this.endDateTimeout = setTimeout(() => {
          this.$store.commit('setDates', {
          endDate: date
          })
        }, 500);
      },
      onTrailingAverageChange (e) {
        this.$store.commit('setDates', {
          trailingAverage: e.target.value
        })
      },
      onCompareChange (e) {
        this.$store.commit('setCompare', {
          compare: e.target.value
        })
      }
    },
    computed: {
      months() { return [
        { name: 'January', value: 0 },
        { name: 'February', value: 1 },
        { name: 'March', value: 2 },
        { name: 'April', value: 3 },
        { name: 'May', value: 4 },
        { name: 'June', value: 5 },
        { name: 'July', value: 6 },
        { name: 'August', value: 7 },
        { name: 'September', value: 8 },
        { name: 'October', value: 9 },
        { name: 'November', value: 10 },
        { name: 'December', value: 11 }
      ] },
      thisMonth() { return (new Date()).getMonth() },
      thisYear() { return (new Date()).getUTCFullYear() },
      years() {
        let yearArray = [];
        for (let i = 2005; i <= (new Date()).getUTCFullYear(); i++) {
          yearArray.push(i)
        }
        return yearArray;
      }
    }
  }
</script>
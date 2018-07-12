<template>
<div class="row" id="controls">
  <div class="col col-12">
    <div class="form">


      <div class="row gutters">
        <div class="col col-7">
          <h4>Configuration</h4>
            <div class="row gutters">
              <div class="col col-6">
                <div class="form-item">
                  <label>Start Date
                    <div class="row gutters">
                      <div class="col col-7">
                        <div class="form-item">
                          <select ref="startMonth" @change=onStartDateChange>
                            <option v-for="month in months" v-bind:value="month.value" v-bind:selected="month.value == thisMonth">{{ month.name }}</option>
                          </select>
                          <div class="desc">Month</div>
                        </div>
                      </div>
                      <div class="col col-5">
                        <div class="form-item">
                          <select ref="startYear" @change=onStartDateChange>
                            <option v-for="year in years" v-bind:value="year" v-bind:selected="year == 2010">{{ year }}</option>
                          </select>
                          <div class="desc">Year</div>
                        </div>
                      </div>
                    </div>
                  </label>
                </div>
            </div>
            <div class="col col-6">
              <div class="form-item">
                <label>End Date
                  <div class="row gutters">
                    <div class="col col-7">
                      <div class="form-item">
                        <select ref="endMonth" @change=onEndDateChange>
                          <option v-for="month in months" v-bind:value="month.value" v-bind:selected="month.value == thisMonth">{{ month.name }}</option>
                        </select>
                        <div class="desc">Month</div>
                      </div>
                    </div>
                    <div class="col col-5">
                      <div class="form-item">
                        <select ref="endYear" @change=onEndDateChange>
                          <option v-for="year in years" v-bind:value="year" v-bind:selected="year == thisYear">{{ year }}</option>
                        </select>
                        <div class="desc">Year</div>
                      </div>
                    </div>
                  </div>
                </label>
              </div>
            </div>
          </div>
          <br>
          <h5>Comparison Options</h5>
            <label>Type
            <div class="form-item form-checkboxes">
              <label class="checkbox"><input name="comparebaseline" value="each" checked type="radio" @change="onCompareChange">Z-score</label><br>
              <label class="checkbox"><input name="comparebaseline" value="percentage" type="radio" @change="onCompareChange">Baseline is compared</label>
            </div>
            <p></p>
            <div class="col col-9">
              <div class="form-item">
                <!-- <input type="text" class="search reposearch" name="headersearch" placeholder="Compared Repository" @change="onComparedRepo"> -->
              </div>
            </div>
            </label>
      </div>
      <div class="col col-5">
        <h4>Rendering</h4>
        <label>Line Charts
        <div class="append">
          <input type="number" min="2" id="averagetimespan" value="180" @change="onTrailingAverageChange"><span>day average</span>
        </div>
        <div class="form-item form-checkboxes">
          <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onRawWeeklyChange">Show raw weekly values<sup class="warn"></sup></label><br>
        </div>
        <div class="form-item form-checkboxes">
          <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onAreaChange">Show area<sup class="warn"></sup></label><br>
        </div>
        <div class="form-item form-checkboxes">
          <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onTooltipChange" checked>Show tooltip<sup class="warn"></sup></label><br>
        </div>
        </label>
        <br>
        <label>Bubble Charts
          <div class="form-item form-checkboxes">
            <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onShowBelowAverageChange">Show users with below-average total contributions<sup class="warn"></sup></label><br>
          </div>
        </label>
        <small class="warn"> - These options affect performance</small>
      </div>

      </div>

    </div>
  </div>
</div>
</template>

<script>
  module.exports = {
    methods: {
      onStartDateChange (e) {
        console.log(e)
        var date = Date.parse((this.$refs.startMonth.value + "/01/" + this.$refs.startYear.value))
        if (this.startDateTimeout) {
          clearTimeout(this.startDateTimeout)
          delete this.startDateTimeout
        }
        this.startDateTimeout = setTimeout(() => {
          console.log(date)
          this.$store.commit('setDates', {
            startDate: date
          })
        }, 500);
      },
      onEndDateChange (e) {
        var date = Date.parse((this.$refs.endMonth.value + "/01/" + this.$refs.endYear.value))
        if (this.endDateTimeout) {
          clearTimeout(this.endDateTimeout)
          delete this.endDateTimeout
        }
        this.endDateTimeout = setTimeout(() => {
          console.log(date)
          this.$store.commit('setDates', {
            endDate: date
          })
        }, 500);
      },
      onTrailingAverageChange (e) {
        this.$store.commit('setVizOptions', {
          trailingAverage: e.target.value
        })
      },
      onRawWeeklyChange (e) {
        this.$store.commit('setVizOptions', {
          rawWeekly: e.target.checked
        })
      },
      onAreaChange (e) {
        this.$store.commit('setVizOptions', {
          showArea: e.target.checked
        })
      },
      onTooltipChange (e) {
        this.$store.commit('setVizOptions', {
          showTooltip: e.target.checked
        })
      },
      onShowBelowAverageChange (e) {
        this.$store.commit('setVizOptions', {
          showBelowAverage: e.target.checked
        })
      },
      onCompareChange (e) {
        this.$store.commit('setCompare', {
          compare: e.target.value
        })
      },
      // onComparedRepo (e) {
      //   this.$store.commit('addComparedRepo', {
      //     githubURL: e.target.value
      //   })
      // }
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

<template>
<div class="row" id="controls">
  <div class="col col-12">
    <div class="form">


      <div class="topic">
        <div class="container">
          <div class="row justify-content-md-center">
            <div class="col col-9">
              <div class="row">
                <div class="col col-3" align="center" id="comparetext"><h6>Compare Repository:</h6></div>

                <div class="col col-9">
                  <input type="text" class="search reposearch" placeholder="GitHub URL" @change="onCompare"/>
                  <p></p>
                </div>
              </div>

            </div>

            <div id="collapse" class="col col-3">
              <div class="col col-12 align-bottom" align="right" v-show="isCollapsed" @click="collapseText">Less configuration options &#9660</div>
              <div class="col col-12 align-bottom" align="right" v-show="!isCollapsed" @click="collapseText">More configuration options &#9654</div>
            </div>

          </div>
        </div>
        <div class="row gutters section collapsible collapsed">
          <div class="col col-5">
            <label>Line Charts
            <div class="row">
              <div class="col col-6">
                <div class="form-item form-checkboxes">
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onRawWeeklyChange">Raw weekly values<sup class="warn"></sup></label>
                </div>
                <div class="form-item form-checkboxes">
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" checked @change="onAreaChange">Standard deviation</label>
                </div>
              </div>
              <div class="col col-6">
                <div class="form-item form-checkboxes">
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onTooltipChange" checked>Show tooltip</label>
                </div>
                <div class="form-item form-checkboxes">
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" checked @change="onDetailChange">Enable detail</label>
                </div>
              </div>
              <label>Bubble Charts
              <div class="form-item form-checkboxes">
                <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onShowBelowAverageChange">Show users with below-average total contributions<sup class="warn"></sup></label><br>
              </div>
              </label>

              <div class="col col-12"><small class="warn"> - These options affect performance</small></div>
              <div class="col col-11"><small>1. Line charts show a rolling mean over {{ info.days }} days with data points at each {{ info.points }}-day interval</small></div>

            </div>
            </label>
          </div>
          <div class="col col-7">
            <div class="row">
              <div class="col col-6">
                <h6>Configuration</h6>
                  <div class="row gutters">
                    <div class="col col-11">
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
                  </div>
                  <p></p>
                  <div class="row gutters">
                    <div class="col col-11">
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

            </div>
            <div class="col col-1"></div>
            <div class="col col-5">
              <h6>Rendering</h6>
              <label>Line Charts<sup>1</sup><sup class="warn"></sup>
              <div class="append col col-10">
                <input type="number" min="20" ref="info" id="averagetimespan" value="180" @change="onTrailingAverageChange" placeholder="180"><span>day average</span>
              </div>
              <p></p>
              <h6>Comparison Type</h6>
                  <label>
                  <div class="form-item form-checkboxes">
                    <label class="checkbox"><input name="comparebaseline" value="zscore" type="radio" @change="onCompareChange">Z-score</label><br>
                    <label class="checkbox"><input name="comparebaseline" value="baseline" checked type="radio" @change="onCompareChange">Baseline is compared</label>
                  </div>
                  </label>
              </label>
              <br>

            </div>
            </div>

          </div>

        </div>
      </div>




      </div>

    </div>
  </div>
</div>
</template>

<script>
  module.exports = {
    data() {
      return {
        info: {
          days: 180,
          points: 45
        },
        isCollapsed: false

      }
    },
    methods: {
      collapseText (){
        this.isCollapsed = !this.isCollapsed;
        if(!this.isCollapsed) {
          $(this.$el).find('.section').addClass('collapsed')
        }
        else $(this.$el).find('.section').removeClass('collapsed')
        // document.querySelector('.section.collapsible').classList.toggle('collapsed')
      },
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
        this.info.days = e.target.value
        this.info.points = e.target.value / 4
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
      onCompare (e) {
        this.$store.commit('addComparedRepo', {
          githubURL: e.target.value
        })
      },
      onDetailChange (e) {
        this.$store.commit('setVizOptions', {
          showDetail: e.target.checked
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

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
                  <option value="January">January</option>
                  <option value="February">February</option>
                  <option value="March">March</option>
                  <option value="April">April</option>
                  <option value="May">May</option>
                  <option value="June">June</option>
                  <option value="July">July</option>
                  <option value="August">August</option>
                  <option value="September">September</option>
                  <option value="October">October</option>
                  <option value="November">November</option>
                  <option value="December">December</option>
                </select>
                <div class="desc">Month</div>
              </div>
            </div>
            <div class="col col-6">
              <div class="form-item">
                <select id="start-year" @change=onStartDateChange>
                  <option value="2005">2005</option>
                  <option value="2006">2006</option>
                  <option value="2007">2007</option>
                  <option value="2008">2008</option>
                  <option value="2009">2009</option>
                  <option value="2010">2010</option>
                  <option value="2011">2011</option>
                  <option value="2012">2012</option>
                  <option value="2013">2013</option>
                  <option value="2014">2014</option>
                  <option value="2015">2015</option>
                  <option value="2016">2016</option>
                  <option value="2017">2017</option>
                  <option value="2018">2018</option>
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
                  <option value="January">January</option>
                  <option value="February">February</option>
                  <option value="March">March</option>
                  <option value="April">April</option>
                  <option value="May">May</option>
                  <option value="June">June</option>
                  <option value="July">July</option>
                  <option value="August">August</option>
                  <option value="September">September</option>
                  <option value="October">October</option>
                  <option value="November">November</option>
                  <option value="December">December</option>
                </select>
                <div class="desc">Month</div>
              </div>
            </div>
            <div class="col col-6">
              <div class="form-item">
                <select id="end-year" @change=onEndDateChange>
                  <option value="2005">2005</option>
                  <option value="2006">2006</option>
                  <option value="2007">2007</option>
                  <option value="2008">2008</option>
                  <option value="2009">2009</option>
                  <option value="2010">2010</option>
                  <option value="2011">2011</option>
                  <option value="2012">2012</option>
                  <option value="2013">2013</option>
                  <option value="2014">2014</option>
                  <option value="2015">2015</option>
                  <option value="2016">2016</option>
                  <option value="2017">2017</option>
                  <option value="2018" selected="selected">2018</option>
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
        var date = Date.parse((document.getElementById("start-month").value + " " + document.getElementById("start-year").value))
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
        var date = Date.parse((document.getElementById("end-month").value + " " + document.getElementById("end-year").value))
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
    }
  }
</script>
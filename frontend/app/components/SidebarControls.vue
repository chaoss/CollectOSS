<template>
  <div class="row" id="controls">
    <div class="col col-12">
      <div class="form">
        <h4>Base Repository</h4>
        <div class="form-item">
          <label>Start Date <input type="date" @change="onStartDateChange"/></label>
        </div>
        <div class="form-item">
          <label>End Date <input type="date" @change="onEndDateChange"/></label>
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
      if (this.startDateTimeout) {
        clearTimeout(this.startDateTimeout)
      }
      this.startDateTimeout = setTimeout(() => {
        this.$store.commit('setDates', {
          startDate: e.target.value
        })
      }, 500);
    },
    onEndDateChange (e) {
      if (this.endDateTimeout) {
        clearTimeout(this.endDateTimeout)
        delete this.endDateTimeout
      }
      this.endDateTimeout = setTimeout(() => {
        this.$store.commit('setDates', {
          endDate: e.target.value
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
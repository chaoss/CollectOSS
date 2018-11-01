<template>
<div class="row" id="controls">
  <div class="col col-12">
    <div class="form">
      

      <div class="topic">
        <div class="container">
          <div class="row justify-content-md-center">
            <div class="col col-9">
              <div class="row">
                <div class="col col-3" align="center" id="comparetext"><h6>Compare from your repos:</h6></div>
                <div class="col col-2">
                  <multiselect class="" v-model="project" :options="projects" :placeholder="project"></multiselect>
                </div>

                <div class="col col-2">
                  <multiselect 
                    v-model="values" 
                    :options="options"
                    :multiple="true"
                    group-label="url"
                    placeholder="Select repos"
                    class="search reposearch "
                    >
                  </multiselect>
                </div>
                <div class="col col-1"><input type="button" @click="onArrayCompare" value="Apply" style="max-width:69.9px"></div>
                <div class="col col-1"><input type="button" @click="onClear" value="Clear" style="max-width:69.9px"></div>
                <div class="col col-3">
                  <input type="text" class="search reposearch" placeholder="Search other GitHub URL" @change="onCompare"/>
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
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" :disabled="disabled" :checked="!disabled" checked @change="onAreaChange">Standard deviation</label>
                </div>
              </div>
              <div class="col col-6">
                <div class="form-item form-checkboxes">
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onTooltipChange" :disabled="disabled" :checked="!disabled" checked>Show tooltip</label>
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
  import Multiselect from 'vue-multiselect'
  module.exports = {
    components: {
      Multiselect
    },
    data() {
      return {
        info: {
          days: 180,
          points: 45
        },
        isCollapsed: false,
        project: "Select project",
        values: [],
        options: [],
        repos: {},
        projects: [],
        disabled: false
      }
    },
    watch: {
      project: function(){
        this.options = []
        this.repos[this.project].forEach(
          (repo) => {this.options.push(repo.url.slice(11))}
        )
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
      onArrayCompare () {
        this.values.forEach(
          (url) => {
            let link = url
            let end = url.slice(url.length - 4)
            console.log("here", end, link)
            if (end == ".git")
              link = link.substring(0, url.length - 4)
              console.log("LINK", link)
            this.$store.commit('addComparedRepo', {
              githubURL: link
            })
          }
        )
      },
      onClear () {
        this.values = []
      },
      onDetailChange (e) {
        this.$store.commit('setVizOptions', {
          showDetail: e.target.checked
        })
      },
      getDownloadedRepos() {
        this.downloadedRepos = []
        window.AugurAPI.getDownloadedGitRepos().then((data) => {
          this.repos = window._.groupBy(data, 'project_name')
          this.projects = Object.keys(this.repos)
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
    },
    mounted() {
      this.getDownloadedRepos()
      window.$(this.$el).find('.multiselect__input').addClass('search')
      window.$(this.$el).find('.multiselect__input').addClass('reposearch')
      if (this.$store.state.comparedRepos.length < 2) this.disabled = true;
    }

  }

</script>

<!-- #SPDX-License-Identifier: MIT -->
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
                <div class="mainControlsDiv1 row col col-4" v-click-outside="stopSelecting">
                  <div class="col col-6 mainControlsDiv2" @click="keepSelecting">

                    <multiselect class="search reposearch special" v-model="project" :options="projects" :placeholder="project"></multiselect>
                  </div>
                  <div class="col col-6 mainControlsDiv2"  @click="keepSelecting">
                    <multiselect 
                      v-model="values" 
                      :options="options"
                      :multiple="true"
                      group-label="url"
                      placeholder="Select repos"
                      class="search reposearch special"
                      >
                    </multiselect>
                  </div>
                </div>
                
                <div class="col col-1"><input type="button" @click="onArrayCompare(); onValuesClear()" value="Apply" class="mainControlsDiv3"></div>
                <div class="col col-1"><input type="button" @click="onClear()" value="Reset" class="mainControlsDiv3"></div>
                <div class="col col-3">
                  <input type="text" class="search reposearch" placeholder="Search other GitHub URL" @change="onCompare"/>
                  <p></p>
                </div>
              </div>

            </div>
                 
                 <!-- <div id="invalid" class="col col-1 invisible invalid-search" align="center">Repo not found.</div> -->

            <div id="collapse" class="col col-3">
              <div class="col col-12 align-bottom" align="right" v-show="isCollapsed" @click="collapseText()">Less configuration options &#9660</div>
              <div class="col col-12 align-bottom" align="right" v-show="!isCollapsed" @click="collapseText()">More configuration options &#9654</div>
            </div>

          </div>
        </div>
        <div class="row gutters section collapsible collapsed">
          <div class="col col-5">
            <label><h6>Line Chart Options</h6>
                <!-- <label><b><t>Show:</t></b></label> -->
            <div class="row">
              <div class="col col-6">
                <div class="form-item form-checkboxes">
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onRawWeeklyChange">Raw weekly values<sup class="warn"></sup></label>
                </div>
                <div class="form-item form-checkboxes">
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" :disabled="!disabled" :checked="disabled" checked @change="onAreaChange">Standard deviation</label>
                </div>
              </div>
              <div class="col col-6">
                <div class="form-item form-checkboxes">
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" @change="onTooltipChange" :disabled="!disabled" :checked="disabled" checked>Show tooltip</label>
                </div>
                <div class="form-item form-checkboxes">
                  <label class="checkbox"><input name="comparebaseline" value="each" type="checkbox" checked @change="onDetailChange">Enable detail</label>
                </div>
              </div>
              <label><h6>Bubble Chart Options </h6>
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
                <h6>Chart Timeline Configuration</h6>
                  <div class="row gutters">
                    <div class="col col-11">
                      <div class="form-item">
                        <label>Start Date
                          <div class="row gutters">
                            <div class="col col-7">
                              <div class="form-item">
                                <select ref="startMonth" @change=onStartDateChange>
                                  <option v-for="month in months" v-bind:value="month.value" v-bind:selected="(startMonth) == month.value">{{ month.name }}</option>
                                </select>
                                <div class="desc">Month</div>
                              </div>
                            </div>
                            <div class="col col-5">
                              <div class="form-item">
                                <select ref="startYear" @change=onStartDateChange>
                                  <option v-for="year in years" v-bind:value="year" v-bind:selected="startYear == year">{{ year }}</option>
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
                              <div class="form-item"> <!--month.value == thisMonth--> <!--year == thisYear--> <!--year == 2010-->
                                <select ref="endMonth" @change=onEndDateChange>
                                  <option v-for="month in months" v-bind:value="month.value" v-bind:selected="(endMonth) == month.value">{{ month.name }}</option>
                                </select>
                                <div class="desc">Month</div>
                              </div>
                            </div>
                            <div class="col col-5">
                              <div class="form-item">
                                <select ref="endYear" @change=onEndDateChange>
                                  <option v-for="year in years" v-bind:value="year" v-bind:selected="endYear == year">{{ year }}</option>
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
                    <label class="checkbox"><input name="comparebaseline" value="zscore" type="radio" :checked="compare == 'zscore'" @change="onCompareChange">Z-score</label><br>
                    <label class="checkbox"><input name="comparebaseline" value="baseline" type="radio" :checked="compare == 'baseline'" @change="onCompareChange">Baseline is compared</label>
                    <label class="checkbox"><input name="comparebaseline" value="rolling" type="radio" :checked="compare == 'rolling'" @change="onCompareChange">Rolling average</label>
                  </div>
                  </label>
              </label>
              <br>

            </div>
            </div>

          </div>

        </div>
      </div>

<!-- :checked="compared"
:checked="!compared"
:checked="!compared" -->


      </div>

    </div>
    <!-- <div style="display: inline-block;">
      <h7 style="display: inline-block;">{{ $store.state.baseRepo }}</h7>
      <h7 style="display: inline-block;" class="repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h7>
      <h7 style="display: inline-block;" v-for="repo in $store.state.comparedRepos">
        <span class="repolisting"> {{ repo }} </span> 
      </h7>
    </div> -->
  </div>
  

</template>



<script>
  import Multiselect from 'vue-multiselect'
  export default {
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
        disabled: false,
        compCount: 0,
        compared: true
      }
    },
    watch: {
      project: function(){
        this.options = []
        this.repos[this.project].forEach(
          (repo) => {
            let url = repo.url
            let first = url.indexOf(".")
            let last = url.lastIndexOf(".")

            let option = null
            if (first == last)
              option = url.slice(url.indexOf('/') + 1)
            else if (url.slice(last) == '.git')
              option = url.slice(url.indexOf('/') + 1)
            else
              option = url.substring(first + 1, last) + repo.url.slice(url.indexOf('/'))
            this.options.push(option)
          }
        )
      },
      compCount: function(){
        if (this.$store.state.comparedRepos.length < 2) this.disabled = true;
        if (this.$store.state.comparedRepos.length == 1) this.compared = true
      }
    },
    directives: {
      'click-outside': {
        bind: function(el, binding, vNode) {
          if (typeof binding.value !== 'function') {
            const compName = vNode.context.name
            let warn = `[Vue-click-outside:] provided expression '${binding.expression}' is not a function, but has to be`
            if (compName) { warn += `Found in component '${compName}'` }
          }
          const bubble = binding.modifiers.bubble
          const handler = (e) => {
            if (bubble || (!el.contains(e.target) && el !== e.target)) {
              binding.value(e)
            }
          }
          el.__vueClickOutside__ = handler
          document.addEventListener('click', handler)
        },
        unbind: function(el, binding) {
          document.removeEventListener('click', el.__vueClickOutside__)
          el.__vueClickOutside__ = null
        }
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

        var date = null
        // Date.parse((this.$refs.startMonth.value + "/01/" + this.$refs.startYear.value))
        if (e.target.value > 12) {
          date = Date.parse((this.startMonth + "/01/" + e.target.value))
        } else {
          let month = (parseInt(e.target.value) + 1).toString()
          date = Date.parse((month + "/01/" + this.startYear))
        }
        if (this.startDateTimeout) {
          clearTimeout(this.startDateTimeout)
          delete this.startDateTimeout
          console.log('startDateTimeout')
        }
        this.startDateTimeout = setTimeout(() => {
          this.$store.commit('setDates', {
            startDate: date
          })
        }, 100);
      },
      onEndDateChange (e) {
        var date = null
        // Date.parse((this.$refs.startMonth.value + "/01/" + this.$refs.startYear.value))
        if (e.target.value > 12) {

          date = Date.parse((this.endMonth + "/01/" + e.target.value))
        } else {
          let month = (parseInt(e.target.value) + 1).toString()
          console.log()
          date = Date.parse((month + "/01/" + this.endYear))
        }
        if (this.endDateTimeout) {
          clearTimeout(this.endDateTimeout)
          delete this.endDateTimeout
        }
        this.endDateTimeout = setTimeout(() => {
          this.$store.commit('setDates', {
            endDate: date
          })
        }, 100);
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
        var element = document.getElementById("invalid")
        this.compCount++
        let repo = window.AugurAPI.Repo({
            githubURL: e.target.value
          })
        if(!repo.batch(['codeCommits'], true)[0]){
          //alert("The repo " + repo.githubURL + " could not be found. Please try again.")
            element.classList.remove("invisible")
        } else {
          this.$store.commit('addComparedRepo', {
            githubURL: e.target.value

          })
           element.classList.add("invisible")

        }
        
      }, 
      onArrayCompare () {
        this.compCount += this.values.length
        this.values.forEach(
          (url) => {
            let link = url
            let end = url.slice(url.length - 4)
            if (end == ".git")
              link = link.substring(0, url.length - 4)
            this.$store.commit('addComparedRepo', {
              githubURL: link
            })
          }
        )
      },
      onValuesClear () {
        this.values = []
      },
      onClear () {
        this.values = []
        this.$store.commit('resetComparedRepos')
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
      },
      keepSelecting() {
        $(this.$el).find('.multiselect__content-wrapper').addClass('selecting')

      },
      stopSelecting() {
        $(this.$el).find('.multiselect__content-wrapper').removeClass('selecting')
        
      }
    },
    computed: {
      compare () {
        return this.$store.state.compare
      },
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
      },
      startMonth() {
        return this.$store.state.startDate.getMonth()
      },
      startYear() {
        return this.$store.state.startDate.getUTCFullYear()
      },
      endMonth() {
        return this.$store.state.endDate.getMonth()
      },
      endYear() {
        return this.$store.state.endDate.getUTCFullYear()
      }
    },
    mounted() {
      this.getDownloadedRepos()
      // $(this.$el).find('.special').addClass('selecting')
      window.$(this.$el).find('.multiselect__input').addClass('search')
      window.$(this.$el).find('.multiselect__input').addClass('reposearch')
      console.log("CHECKING", this.$store.state.startDate.getMonth(), this.$store.state.startDate.getUTCFullYear(), this.$store.state.endDate.getMonth(), this.$store.state.endDate.getUTCFullYear())

      if (this.projects.length == 1) this.project = this.projects[0]
    }

  }

</script>

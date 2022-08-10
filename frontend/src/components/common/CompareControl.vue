<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-container style="max-width: 1240px; padding-bottom:1rem">
    <d-card>
      <d-card-header>
        <d-row class="align-items-center">
          <d-col cols="12" lg="2">
            <div class="text-center text-lg-center ">Compare from your repos:</div>
          </d-col>
          <d-col cols="12" lg="4">
            <multiselect v-model="selectedGroups" :options="GroupOptions"
                         placeholder="Select Group" :close-on-select="false" :clear-on-select="false"
                         :preserve-search="true"  :multiple="isGroup">
              <template slot="selection" slot-scope="{ values, search, isOpen }"><span
                class="multiselect__single" v-if="values.length && !isOpen">{{ values.length }} options selected</span>
              </template>
            </multiselect>
          </d-col>
          <d-col cols="12" lg="4" v-if="!isGroup">
            <multiselect v-model="selectedRepos" :multiple="true" :close-on-select="false" :clear-on-select="false"
                         :preserve-search="true" :options="RepoOptions"
                         :disabled="getSelectedGroups.length === 0" placeholder="Select Repo" >
              <template slot="selection" slot-scope="{ values, search, isOpen }"><span
                class="multiselect__single" v-if="values.length && !isOpen">{{ values.length }} options selected</span>
              </template>
              <template slot="option" slot-scope="props">
                <div class="option__desc">{{ props.option.split('/')[1] }}</div>
              </template>
            </multiselect>
          </d-col>
          <d-col cols="12" lg="1">
            <d-button-group size="small">
              <d-button @click="onCompare">Apply</d-button>
              <d-button @click="onReset">Reset</d-button>
            </d-button-group>
          </d-col>
          
          <!-- <d-col cols="12" lg="3" :class="{'offset-md-3':isGroup}">
            <div v-d-toggle.my-collapse variant="primary" size="small" class="float-right"
                 @click="isCollpase = !isCollpase">
               <div v-if="isCollpase">More configuration options<i class="material-icons" style="font-size: 1.3rem
">keyboard_arrow_down</i></div>
               <div v-if="!isCollpase">Less configuration options<i class="material-icons" style="font-size: 1.3rem">keyboard_arrow_up</i>
              </div>
            </div>
          </d-col> -->
         
        </d-row>
        <d-row>
            <d-badge theme="primary" v-if="!isGroup" pill class="mx-2 mt-2" v-for="item in getSelectedRepos">
              {{item}}
              <a @click="removeSelectedRepos(item)">&nbsp;&nbsp;x</a>
            </d-badge>
            <d-badge theme="primary" v-if="isGroup" pill class="mx-2 mt-2" v-for="item in getSelectedGroups">
              {{item}}
              <a @click="removeSelectedGroups(item)">&nbsp;&nbsp;x</a>
            </d-badge>
        </d-row>
      </d-card-header>
      <d-collapse id="my-collapse">
        <d-card-body>
          <d-row>
            <d-col cols="5">
              <div>
                <label class="d-block">
                  <div style="font-size: 18px;font-weight:500;" class="mb-3">
                    Line Chart Options
                  </div>
                  <d-row>
                    <d-col>
                      <d-form-checkbox name="comparebaseline" :checked="rawWeekly" @change="onRawWeeklyChange">Raw
                        weekly values
                      </d-form-checkbox>
                      <d-form-checkbox name="comparebaseline" :checked="showArea" @change="onAreaChange">Standard
                        deviation
                      </d-form-checkbox>
                    </d-col>
                    <d-col>
                      <d-form-checkbox name="comparebaseline" :checked="showTooltip" @change="onTooltipChange">Show
                        tooltip
                      </d-form-checkbox>
                      <d-form-checkbox name="comparebaseline" :checked="showDetail" @change="onDetailChange">Enable
                        detail
                      </d-form-checkbox>
                    </d-col>
                  </d-row>
                </label>
                <label>
                  <div style="font-size: 18px;font-weight:500;" class="mb-3">Bubble Chart Options</div>
                  <d-row>
                    <d-col>
                      <d-form-checkbox name="comparebaseline" :checked="showBelowAverage"
                                       @change="onShowBelowAverageChange" inline>Show users with below-average total
                        contributions
                      </d-form-checkbox>
                      <sup class="warn"></sup>
                    </d-col>
                  </d-row>
                </label>
                <d-row>
                  <d-col cols="12">
                    <div class="col col-12"><small class="warn"> - These options affect performance</small></div>
                    <div class="col col-11"><small>1. Line charts show a rolling mean over {{ trailingAverage }} days
                      with data points at each {{ trailingAverage/4 }}-day interval</small></div>
                  </d-col>
                </d-row>
              </div>
            </d-col>
            <d-col cols="7">
              <d-row>
                <d-col cols="6">
                  <div style="font-size: 18px;font-weight:500;" class="mb-3">Chart Timeline Configuration</div>
                  <d-row>
                    <d-col>
                      <div>Start Date</div>
                      <d-datepicker
                        :value="startDate"
                        :disabled-dates="disabledDates"
                        @selected="onStartDate"
                        typeable/>
                    </d-col>
                  </d-row>
                  <d-row>
                    <d-col>
                      <div>End Date</div>
                      <d-datepicker
                        :value="endDate"
                        :disabled-dates="disabledDates"
                        @selected="onEndDate"
                        typeable/>
                    </d-col>
                  </d-row>
                </d-col>
                <d-col cols="5" offset-md="1">
                  <d-row>
                    <div style="font-size: 18px;font-weight:500;" class="mb-3">Rendering</div>
                  </d-row>
                  <d-row>
                    <d-col>
                      <div>Start Date</div>
                      <d-input-group append="day average" class="mb-3">
                        <d-form-input type="number" :value="trailingAverage"
                                      @change="onTrailingAverageChange"></d-form-input>
                      </d-input-group>
                    </d-col>
                  </d-row>
                  <d-row>
                    <d-col>
                      <div style="font-size: 18px;font-weight:500;">Comparison Type</div>
                      <d-form-radio name="comparebaseline" value="zscore" :checked="compare === 'zscore'"
                                    @change="setCompare">Z-score
                      </d-form-radio>
                      <d-form-radio name="comparebaseline" value="baseline" :checked="compare === 'baseline'"
                                    @change="setCompare">Baseline is compared
                      </d-form-radio>
                      <d-form-radio name="comparebaseline" value="rolling" :checked="compare === 'rolling'"
                                    @change="setCompare">Rolling average
                      </d-form-radio>
                    </d-col>
                  </d-row>
                </d-col>
              </d-row>
            </d-col>
          </d-row>
        </d-card-body>
      </d-collapse>
    </d-card>
  </d-container>
</template>


<script lang="ts">
  import Multiselect from 'vue-multiselect';
  import {Component, Vue, Watch} from 'vue-property-decorator';
  import {mapActions, mapGetters, mapMutations} from "vuex";
  import router from '@/router'
  import style from "vega-embed/src/style";
  import {keys} from "vega-lite/build/src/util";

  @Component({
    components: {
      Multiselect,
    },
    computed: {
      ...mapGetters('common', [
        'repos',
        'repoGroups',
        'repoRelations'
      ]),
      ...mapGetters('compare', [
        'base',
        'compare',
        'trailingAverage',
        'rawWeekly',
        'showTooltip',
        'showArea',
        'showDetail',
        'showBelowAverage',
        'startDate',
        'endDate',
        'isGroup',
        'comparedRepos',
        'comparedRepoGroups',
        'comparisionSize',
      ])
    },
    methods: {
      ...mapMutations('common', [
        'mutateStartDate', 
        'mutateEndDate'        
      ]), 
      ...mapMutations('compare', [
        'setCompare',
        'setVizOptions',
        'resetCompared',
        'mutateComparedRepo',
        'mutateComparedGroup'
      ]),
      ...mapActions('compare',[
        'setComparedRepos',
        'setComparedGroup',
        'setBaseGroup',
        'setBaseRepo'
      ]),
      ...mapActions('common', [
        'loadRepoGroups',
        'loadRepos',
      ])
    }
  })

  export default class CompareControl extends Vue {
    selectedGroups: any = []
    selectedRepos: any = []
    GroupOptions: string[] = []
    loadedGroups: boolean = false;
    loadedRepos: boolean = false;

    isCollpase: boolean = true
    options: string[] = ['list', 'of', 'options']
    disabledDates: any = {
      // Disable all the dates up to specific date.
      to: new Date(2011, 0, 1),

      // Disable all dates after specific date.
      from: new Date(),
    }

    //decalre for vuex state
    base!: any
    compare!: any;
    trailingAverage!: number;
    setVizOptions!: any;
    rawWeekly!: boolean;
    showTooltip!: boolean;
    showArea!: boolean;
    showDetail!: boolean;
    showBelowAverage!: boolean;
    startDate!: Date;
    endDate!: Date;
    isGroup!: boolean;


    comparedRepoGroups!:any;
    comparedRepos!:any;
    comparisionSize!:any;

    mutateStartDate!: any;
    mutateEndDate!: any;
    mutateComparedRepo!:any;
    mutateComparedGroup!:any;
    setCompare!:any;

    setComparedRepos!:any;
    setComparedGroup!:any;
    setBaseRepo!:any;
    setBaseGroup!:any;


    loadRepoGroups!: any;
    loadRepos!: any;

    resetCompared!: any;
    repoRelations!: any;
    repoGroups!: any;


    created() {
      // if not cached, load repo groups and repos
      if (!this.loadedGroups) {
        this.loadRepoGroups().then(() => {
          let rg_names:string[] = []
          this.repoGroups.forEach((rg:any) => {
            rg_names.push(rg.rg_name)
          })
          this.GroupOptions = rg_names
          this.loadedGroups = true
        })
      }
      // when comparision is group type, we don't need to load repos
      if (!this.isGroup && !this.loadedRepos) {
        this.loadRepos().then(() => {
          this.loadedRepos = true
        })
      }

      this.selectedRepos = this.comparedRepos
      this.selectedGroups = this.comparedRepoGroups
    }

    get getSelectedGroups() {
      return this.selectedGroups
    }

    get getSelectedRepos() {
      return this.selectedRepos.names
    }

    get selectedRepoEntities () {
      console.log("Compare control")
      let repos: any[] = []
      let repo = null
      let i = null
      for (i in this.selectedRepos) {
        repo = this.selectedRepos[i]
        console.log(repo, this.repoRelations, this.selectedGroups)
        console.log(this.repoRelations[this.selectedGroups][repo.split('/')[1]])
        repos.push(this.repoRelations[this.selectedGroups][repo.split('/')[1]])
      }
      return repos
    }

    // get GroupOptions() {
    //   let rg_names:string[] = []
    //   this.repoGroups.forEach((rg:any) => {
    //     console.log("GROUP")
    //     rg_names.push(rg.rg_name)
    //   })
    //   return rg_names
    // }

    get RepoOptions() {
      let repos =  Object.values(this.repoRelations[this.selectedGroups] || [])
      let names:string[] = []
      repos.forEach((repo:any)=> {
        names.push(this.selectedGroups + '/' + repo.repo_name)
      })
      return names
    }


    onTrailingAverageChange(e: any) {
      this.setVizOptions({
        trailingAverage: e
      })
    }

    onRawWeeklyChange(checked: any) {
      this.setVizOptions({
        rawWeekly: checked ? true : false
      })
    }

    onDetailChange(e: any) {
      this.setVizOptions({
        showDetail: e ? true : false
      })
    }

    onAreaChange(e: any) {
      this.setVizOptions({
        showArea: e ? true : false
      })
    }

    onTooltipChange(e: any) {
      this.setVizOptions({
        showTooltip: !this.showTooltip
      })
    }

    onShowBelowAverageChange(e: any) {
      this.setVizOptions({
        showBelowAverage: !this.showBelowAverage
      })
    }

    onStartDate(e: any) {
      this.mutateStartDate(e)
    }

    onEndDate(e: any) {
      this.mutateEndDate(e)
    }

    onCompare(e: any) {
      // ensure that a repository is selected
      if (this.selectedRepos.length === 0) {
        window.alert('Please select a repo first from the dropdown');
        return;
      }
      if (!this.isGroup) {
        console.log("onCompare: ", e, this.base)
        let comparedRepoIds = ''//String(this.base.repo_id)
        let repo: any = null
        let i = 0
        for (repo of this.selectedRepoEntities) {
          console.log(repo)
          if (i == 0)
            comparedRepoIds += String(repo.repo_id)
          else
            comparedRepoIds += "," + String(repo.repo_id)
          i++
        }
        this.setComparedRepos({ 'names': [this.selectedRepos.join(',')], 'ids': [comparedRepoIds] }).then(() => {
          router.push({
            name: 'repo_overview_compare',
            params: {
              group: this.base.rg_name,
              repo: this.base.repo_name,
              repo_group_id: this.base.repo_group_id,
              repo_id: this.base.repo_id,
              compares: this.selectedRepos.join(','),
              comparedRepoIds
            }
          })
        })

      } else {
        router.push({
          name: 'group_overview_compare',
          params: {group: this.base.rg_name, repo_group_id: this.base.repo_group_id, compares:
              this.selectedGroups.join(',')}
        })
      }
    }

    onReset() {
      this.selectedGroups = []
      this.selectedRepos = []
      let initialState: any = {
        startDate: new Date('1 February 2011'),
        endDate: new Date(),
        trailingAverage: 180,
        compare: 'rolling',
        rawWeekly: false,
        showArea: true,
        showDetail: false,
        showTooltip: true,
        byDate: false,
        showBelowAverage: false,
      }
      this.setVizOptions(
        initialState
      )
      this.mutateStartDate(initialState.startDate)
      this.mutateEndDate(initialState.endDate)
      this.resetCompared()

      if (!this.isGroup) {
        router.push({
          name: 'repo_overview',
          params: {group: this.base.rg_name, repo: this.base.repo_name}
        })
      } else {
        router.push({
          name: 'group_overview',
          params: {group: this.base.rg_name}
        })
      }
    }

    removeSelectedRepos(e:any) {
      let index = this.selectedRepos.indexOf(e);
      if (index !== -1) this.selectedRepos.splice(index, 1);
    }

    removeSelectedGroups(e:any) {
      let index = this.selectedGroups.indexOf(e);
      if (index !== -1) this.selectedGroups.splice(index, 1);
    }
  }
</script>

<style scoped>
  @import "../../../node_modules/vue-multiselect/dist/vue-multiselect.min.css";
</style>

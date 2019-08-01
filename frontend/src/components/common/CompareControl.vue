<template>
  <d-container>
    <d-card>
      <d-card-header>
        <d-row class="align-items-center">
          <d-col cols="12" lg="2">
            <div class="text-center text-lg-center ">Compare from your repos:</div>
          </d-col>
          <d-col cols="12" lg="3">
            <multiselect v-model="selectedGroups" track-by="rg_name" label="rg_name" :options="GroupOptions"
                         placeholder="Select Group">
              <template slot="singleLabel" slot-scope="{ option }">{{option.rg_name}}</template>
            </multiselect>
          </d-col>
          <d-col cols="12" lg="3" v-if="!isGroup">
            <multiselect v-model="selectedRepos" :multiple="true" :close-on-select="false" :clear-on-select="false"
                         :preserve-search="true" :options="RepoOptions" track-by="repo_name" label="repo_name"
                         :disabled="getSelectedGroups.length === 0" placeholder="Select Repo" >
              <template slot="selection" slot-scope="{ values, search, isOpen }"><span
                class="multiselect__single" v-if="values.length && !isOpen">{{ values.length }} options selected</span>
              </template>
            </multiselect>
          </d-col>
          <d-col cols="12" lg="1">
            <d-button-group size="small">
              <d-button>Apply</d-button>
              <d-button @click="onReset">Reset</d-button>
            </d-button-group>
          </d-col>
          <d-col cols="12" lg="3" :class="{'offset-md-4':isGroup}">
            <div v-d-toggle.my-collapse variant="primary" size="small" class="float-right"
                 @click="isCollpase = !isCollpase">
              <div v-if="isCollpase">More configuration options<i class="material-icons" style="font-size: 1.3rem
">keyboard_arrow_down</i></div>
              <div v-if="!isCollpase">Less configuration options<i class="material-icons" style="font-size: 1.3rem">keyboard_arrow_up</i>
              </div>
            </div>
          </d-col>
        </d-row>
        <d-row>
            <d-badge theme="primary" v-if="!isGroup" pill class="mx-2 mt-2" v-for="item in getSelectedRepos">
              {{item.rg_name + '/'+item.repo_name}}
              <a @click="removeSelectedRepos(item)">&nbsp;&nbsp;x</a>
            </d-badge>
            <d-badge theme="primary" v-if="isGroup" pill class="mx-2 mt-2" v-for="item in getSelectedGroups">
              {{item.rg_name}}
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
  import {Component, Vue} from 'vue-property-decorator';
  import {mapActions, mapGetters, mapMutations} from "vuex";
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
        'loaded_repos',
        'loaded_groups',
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
      ])
    },
    methods: {
      ...mapMutations('compare', [
        'setCompare',
        'setVizOptions',
        'mutateStartDateChange',
        'mutateEndDateChange',
        'resetCompared',
        'mutateComparedRepo',
        'mutateComparedGroup'
      ]),
      ...mapActions('common', [
        'loadRepoGroups',
        'loadRepos',
      ])
    }
  })

  export default class CompareControl extends Vue {
    selectedGroups: any = [];
    selectedRepos: any = [];
    isCollpase: boolean = true;
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
    loaded_repos!: boolean;
    loaded_groups!: boolean;
    comparedRepoGroups!:any;
    comparedRepos!:any;

    mutateStartDateChange!: any;
    mutateEndDateChange!: any;
    mutateComparedRepo!:any;
    mutateComparedGroup!:any;
    setCompare!:any;


    loadRepoGroups!: any;
    loadRepos!: any;

    resetCompared!: any;
    repoRelations!: any;
    repoGroups!: any;


    mounted() {
      // if not cached, load repo groups and repos
      if (!this.loaded_groups) {
        this.loadRepoGroups()
      }
      // when comparision is group type, we don't need to load repos
      if (!this.isGroup && !this.loaded_repos) {
        this.loadRepos()
      }

      this.selectedRepos = this.comparedRepos
      this.selectedGroups = this.comparedRepoGroups
    }

    get getSelectedGroups() {
      return this.selectedGroups
    }

    get getSelectedRepos() {
      return this.selectedRepos
    }

    get GroupOptions() {
      return this.repoGroups
    }

    get RepoOptions() {

      let group = this.selectedGroups || {}
      let rg_name = group.rg_name || []

      console.log("1111", this.selectedGroups, group, rg_name)
      return Object.values(this.repoRelations[rg_name] || [])
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
      this.mutateStartDateChange(e)
    }

    onEndDate(e: any) {
      this.mutateEndDateChange(e)
    }

    onCompare(e: any) {
      if(!this.isGroup) {
        this.mutateComparedRepo(this.selectedRepos)
      } else {

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
      this.mutateStartDateChange(initialState.startDate)
      this.mutateEndDateChange(initialState.endDate)
      this.resetCompared()
    }
    removeSelectedRepos(e:any) {
      let index = this.selectedRepos.indexOf(e);
      if (index !== -1) this.selectedRepos.splice(index, 1);
    }
    removeSelectedGroups(e:any){
      let index = this.selectedGroups.indexOf(e);
      if (index !== -1) this.selectedGroups.splice(index, 1);
    }
  }
</script>

<style scoped>
  @import "../../../node_modules/vue-multiselect/dist/vue-multiselect.min.css";
</style>
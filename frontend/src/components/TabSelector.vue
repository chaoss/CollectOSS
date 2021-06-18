<!-- #SPDX-License-Identifier: MIT -->
<template>

	<d-button-group vertical>
      	<d-button outline :active="tab == 'repo_overview'" class="tabSelectorButton" @click="onTab" value="repo_overview">Overview</d-button>
      	<d-button outline :active="tab == 'repo_risk'" class="tabSelectorButton" theme="secondary" @click="onTab" value="repo_risk">Risk Metrics</d-button>
      	<d-button v-if="getComparedReposNames.length > 0" outline :active="tab == 'repo_overview_compare'" class="tabSelectorButton"theme="info" @click="onTab" value="repo_overview_compare">Comparison</d-button>
    </d-button-group>
</template>

<script lang="ts">
import { mapActions, mapGetters, mapMutations } from "vuex";
import Component from 'vue-class-component';
import Vue from 'vue';

@Component({
  methods: {
    ...mapMutations('compare', [
      'setVizOptions',
      'mutateStartDateChange',
      'mutateEndDateChange',
      'resetCompared',
    ]),
  },
  computed: {
    ...mapGetters('common', [
    	'tab'
    ]),
    ...mapGetters('compare',[
		'base',
		'comparedRepos'
    ]),
  },
})
export default class TabSelector extends Vue {

	//getters
	tab!:any
	base!:any
	comparedRepos!:any

  mutateStartDateChange!: any;
  mutateEndDateChange!: any;

  setVizOptions!: any;

  resetCompared!: any;

  get getComparedReposNames () {
    return this.comparedRepos.names || []
  }

  onReset() {
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

	onTab(e: any) {
	    console.log("onTab", e.target.value)
      // let names = ''
      // if (e.target.value == 'repo_overview_compare') {

      //   this.comparedRepos.forEach((repo:any) => {
      //     names += repo.rg_name + '/' + repo.repo_name
      //   })
      // }
      // if (names == '') names = 'none_selected'
      this.onReset()
      let ref = this.base.repo_name || this.base.url
	    this.$router.push({
	      	name: e.target.value, params: {repo: ref, group: this.base.rg_name}//, compares: names}
	    })
	}
}
</script>

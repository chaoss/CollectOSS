<template>

	<d-button-group vertical>
      	<d-button outline :active="tab == 'repo_overview'" style="font-size: 0.8rem" @click="onTab" value="repo_overview">Overview</d-button>
      	<d-button outline :active="tab == 'repo_risk'" style="font-size: 0.8rem" theme="secondary" @click="onTab" value="repo_risk">Risk Metrics</d-button>
      	<d-button outline :active="tab == 'repo_overview_compare'" style="font-size: 0.8rem" theme="info" @click="onTab" value="repo_overview_compare">Comparison</d-button>
    </d-button-group>
</template>

<script lang="ts">
import { mapActions, mapGetters, mapMutations } from "vuex";
import Component from 'vue-class-component';
import Vue from 'vue';

@Component({
  methods: {
    ...mapActions('common',[

    ])
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

	onTab(e: any) {
	    console.log("onTab", e.target.value)
	    this.$router.push({
	      	name: e.target.value, params: {repo: this.base.repo_name, group: this.base.rg_name}
	    })
	}
}
</script>

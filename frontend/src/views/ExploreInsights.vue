<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-container fluid class="main-content-container px-4">

    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <span class="text-uppercase page-subtitle">Exploring Insights Feature</span>
        <h3 class="page-title">Coming Soon!</h3>
      </div>
    </div>

  </d-container>
</template>

<script lang="ts">
import Component from 'vue-class-component';
import Vue from 'vue';
import {mapActions, mapGetters, mapMutations} from "vuex";
import Spinner from '../components/Spinner.vue'
@Component({
  components: {
    Spinner,
  },
  methods: {
    ...mapActions('common',[
      'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                  // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
      'getRepoRelations',
      'loadRepos',
      'addRepo'
    ]),

    ...mapActions('compare',[
      'addComparedRepo',
      'setBaseRepo'
    ])
  },
  computed: {
    ...mapGetters('common', [
      'sortedRepos'
    ]),
  },
})

export default class Workers extends Vue{
  colors: string[] = ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"];
  // repos: any[] = [];
  repo_groups:any[] = [];
  repo_relations:any[] =  [];
  themes: string[] = ['dark', 'info', 'royal-blue', 'warning'];
  loadedGroups: boolean = false;
  loadedSparks: boolean = false;
  loadedRepos: boolean = false;

  ascending:boolean = false;
  sortColumn: string ='name';


  getRepoRelations!: any
  sortedRepos!:any
  loadRepos!:any;
  
  addRepo!:any;
  setBaseRepo!:any;
  addComparedRepo!:any;


  created() {
    
  }
  
  sortTable(col: string) {
      if (this.sortColumn === col) {
        this.ascending = !this.ascending;
      } else {
        this.ascending = true;
        this.sortColumn = col;
      }
  }

}

</script>


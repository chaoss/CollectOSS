<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>

      <div v-if="loaded">
        <p v-if="values == undefined || values.length == 0">There is no CII Best Practices data for this repository</p>
        <p v-for="el in values">
          <img :src="'https://bestpractices.coreinfrastructure.org/projects/' + el.id + '/badge'" width = 40%>
          <br><br>
          The badge status of <strong>{{el.repo_name}}</strong> is <strong>{{el.badge_level}}</strong>
          <br> This information was last updated on <strong>{{el.date.split("T")[0]}}</strong>
          <br> The CII ID is <strong>{{el.id}}</strong>
          <br> More CII data for this project can be found at CII's <a :href="'https://bestpractices.coreinfrastructure.org/projects/' + el.id">best practices badging website.</a>
        </p>
      </div>
    </d-card-body>
  </d-card>
</template>

<script lang="ts">
  import Spinner from '@/components/Spinner.vue'
  import  { Component, Vue } from 'vue-property-decorator';
  import {mapActions, mapGetters} from "vuex";

  const AppProps = Vue.extend({
    props: {
      title: String,
      data: Object,
      source: String,
      headers: Array,
      fields: Array,
    }
  })

  @Component({
    components: {
      Spinner
    },
    computed: {
      ...mapGetters('compare',[
        'comparedRepos',
        'base'
      ]),
    },
    methods: {
      ...mapActions('common',[
        'endpoint', // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                    // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
      ]),
    }
  })
  export default class CountBlock extends AppProps{

    // data props
    loaded: boolean = false
    values: any[] = []
    
    // compare getters
    base!:any
    comparedRepos!:any

    // common actions
    endpoint!:any

    created () {
      if (this.data) {
        this.loaded = true
        this.values = this.data[this.source]
      }
      
      else {
        this.endpoint({endpoints:[this.source],repos:[this.base]}).then((tuples:any) => {
          let ref = this.base.url || this.base.repo_name
          let values:any = []
          Object.keys(tuples[ref]).forEach((endpoint) => {
            values = tuples[ref][endpoint]
          })
          this.values = values
          this.loaded = true
        })
      }
    }

  }
</script>

<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>
      <span v-if="loaded" class="countBlockSpan">{{ count }}</span>

    </d-card-body>
    </d-card>
    </template>

    <script lang="ts">
  import  { Component, Vue } from 'vue-property-decorator';
  import {mapActions, mapGetters} from "vuex";
  import Spinner from '@/components/Spinner.vue'

  const AppProps = Vue.extend({
    props: {
      title: String,
      data: Object,
      source: String,
      field: String,
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
    count: any[] = []
    
    // compare getters
    base!:any
    comparedRepos!:any

    // common actions
    endpoint!:any

    created () {
      if (this.data) {
        this.loaded = true
        this.count = this.data[this.source][0][this.field]
      }
      
      else {
        this.endpoint({endpoints:[this.source],repos:[this.base]}).then((tuples:any) => {
          let ref = this.base.url || this.base.repo_name
          let values:any = []
          Object.keys(tuples[ref]).forEach((endpoint) => {
            values = tuples[ref][endpoint]
          })
          this.count = values[0][this.field]
          console.log("countblock", values, this.count)
          this.loaded = true          
        })
      }
    }

  }
</script>

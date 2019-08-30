<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <p v-for="el in values">
      <img :src="'https://bestpractices.coreinfrastructure.org/projects/' + el.id + '/badge'" width = 40%>
      <br><br>
      The badge status of <strong>{{el.repo_name}}</strong> is <strong>{{el.badge_level}}</strong>
      <br> This information was last updated on <strong>{{el.date.split("T")[0]}}</strong>
      <br> The CII ID is <strong>{{el.id}}</strong>
      <br> More CII data for this project can be found at CII's <a :href="'https://bestpractices.coreinfrastructure.org/projects/' + el.id">best practices badging website.</a>

      </p>
    </d-card-body>
  </d-card>
</template>

<script lang="ts">
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
    computed: {
      ...mapGetters('compare',[
        'comparedRepos',
        'base'
      ]),
    },
  })
  export default class CountBlock extends AppProps{

    // compare.getter
    base!:any
    comparedRepos!:any


    get values(){
      return this.data[this.source]
    }

  }
</script>

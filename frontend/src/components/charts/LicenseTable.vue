<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <table style="width: 100%">
        <thead class="bg-light">
          <th v-for="header in headers">{{header}}</th>
        </thead>
        <tbody>
          <tr v-for="el in values">
            <td v-for="field in fields">{{el[field]}}</td>
          </tr>
        </tbody>
      </table>
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
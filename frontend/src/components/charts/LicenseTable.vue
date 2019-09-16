<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
    <strong><p> Click on the names of highlighted licenses to learn more.</p></strong>
      <table style="width: 100%">
        <thead class="bg-light">
          <th v-for="header in headers">{{header}}</th>
        </thead>
        <tbody>
          <tr v-for="el in values">
            <a v-bind:href="ldata[0][el['short_name']]" target="_blank">
              <td>{{el['short_name']}}</td>
            </a>
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
      ldata: Array,
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

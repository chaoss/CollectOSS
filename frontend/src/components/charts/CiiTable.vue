<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>
      <div v-if="loaded">
        <p v-if="values == undefined || values.length == 0">There is no CII Best Practices data for this
          repository</p>
        <div v-for="value in values">
          <img :src="'https://bestpractices.coreinfrastructure.org/projects/' + value.id + '/badge'"
               alt="badge-image" width=40%>
          <br>
          <br>
          <span>The badge status of this repository is</span><strong>{{value.badge_level}}</strong>
          <br>
          <span>The CII ID is </span><strong>{{value.id}}</strong>
          <br>
          <span>More CII data for this project can be found at CII's </span>
          <a :href="'https://bestpractices.coreinfrastructure.org/projects/' + value.id">best practices
            badging website.</a>
        </div>
      </div>
    </d-card-body>
  </d-card>
</template>

<script lang="ts">
  import Spinner from "@/components/Spinner.vue"
  import { Component, Vue } from "vue-property-decorator";
  import { mapActions, mapGetters } from "vuex";

  const AppProps = Vue.extend({
    props: {
      title: String,
      data: Object,
      source: String,
      headers: Array,
      fields: Array,
    }
  });

  @Component({
    components: {
      Spinner
    },
    computed: {
      ...mapGetters("compare", [
        "comparedRepos",
        "base"
      ]),
    },
    methods: {
      ...mapActions("common", [
        "endpoint", // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
                    // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
      ]),
    }
  })
  export default class CountBlock extends AppProps {

    // data props
    loaded: boolean = false;
    values: any[] = [];

    // compare getters
    base!: any;
    comparedRepos!: any;

    // common actions
    endpoint!: any;

    created() {
      if (this.data) {
        this.loaded = true;
        this.values = this.data[this.source]
      } else {
        this.endpoint({endpoints: [this.source], repos: [this.base]}).then((tuples: any) => {
          let ref = this.base.url || this.base.repo_name;
          let values: any = [];
          Object.keys(tuples[ref]).forEach((endpoint) => {
            values = tuples[ref][endpoint]
          });
          this.values = values;
          this.loaded = true
        })
      }
    }

  }
</script>

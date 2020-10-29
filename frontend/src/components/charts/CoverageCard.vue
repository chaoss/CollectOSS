<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!allLoaded"></spinner>
      <div v-if="allLoaded">
        <p v-if="values.length == 0 || values == undefined">There are no license coverage metrics available for
          this repository.</p>
        <div v-else>
          <h4>{{ UsableValues[2] }}%</h4>
          <div class="coverageCardDiv1">
            <p> Total Files
              <br>
              <span>Files with Declared Licenses</span>
              <br>
              <span>Files without Licenses</span>
            </p>
          </div>
          <div class="coverageCardDiv2">
            <p>
              <strong>
                <span>{{ UsableValues[0] }}</span>
                <br>
                <span>{{ UsableValues[1] }}</span>
                <br>
                <span>{{ UsableValues[3] }}</span>
              </strong>
            </p>
          </div>
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
      dataTwo: Object,
      sourceTwo: String,
      headers: Array,
      fields: Array,
    }
  });

  @Component({
    components: {
      Spinner
    },
    computed: {
      allLoaded: function () {
        // @ts-ignore
        return this.loaded && this.loaded2;
      },
      UsableValues: function () {
        let licenseCount = 0;
        // @ts-ignore
        for (let el of this.valuesTwo) {
          let shortName = el["short_name"];
          if (shortName != "No Assertion") {
            licenseCount += el["count"]
          }
        }
        // @ts-ignore
        const totalFiles = this.values[0]["sbom_scan"]["License Coverage"]["TotalFiles"];
        let percent = (licenseCount / totalFiles) * 100;
        let fixed = Math.pow(10, 2 || 0);
        let licenseCoverage = Math.floor(percent * fixed) / fixed;
        let differenceCount = totalFiles - licenseCount;
        return [totalFiles, licenseCount, licenseCoverage, differenceCount]
      },
      ...mapGetters("compare", [
        "comparedRepos",
        "base"
      ]),
    },
    methods: {
      ...mapActions("common", [
        "endpoint",
      ]),
    }
  })
  export default class CountBlock extends AppProps {

    // data props
    loaded: boolean = false;
    loaded2: boolean = false;
    values: any[] = [];
    valuesTwo: any[] = [];

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
          if (ref.includes("/")) {
            ref = ref.split("/")[ref.split("/").length - 1]
          }
          let values: any = [];
          Object.keys(tuples[ref]).forEach((endpoint) => {
            values = tuples[ref][endpoint]
          });
          this.values = values;
          this.loaded = true
        })
      }

      if (this.dataTwo) {
        this.loaded2 = true;
        this.valuesTwo = this.dataTwo[this.sourceTwo]
      } else {
        this.endpoint({endpoints: [this.sourceTwo], repos: [this.base]}).then((tuples: any) => {
          let ref = this.base.url || this.base.repo_name;
          if (ref.includes("/")) {
            ref = ref.split("/")[ref.split("/").length - 1]
          }
          let valuesTwo: any = [];
          Object.keys(tuples[ref]).forEach((endpoint) => {
            valuesTwo = tuples[ref][endpoint]
          });
          this.valuesTwo = valuesTwo;
          this.loaded2 = true
        })
      }

    }
  }
</script>

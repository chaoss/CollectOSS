<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>
      <div v-if="loaded">
        <p>
          <strong>Click on a license for a description of the license</strong>
        </p>
        <p>
          <strong>Click on a license count to download a list of associated files</strong>
        </p>
        <table class="licenseTable">
          <thead style="border:2pt solid #f7f7f7;" class="bg-light">
          <tr>
            <th v-for="header in headers">{{header}}</th>
          </tr>
          </thead>
          <tbody style="border:2pt solid #f7f7f7;">
          <tr style="border-bottom:1.5pt solid #f7f7f7;" v-for="el in values">
            <td><a v-bind:href="ldata[0][el['short_name']]" target="_blank">{{el['short_name']}}</a></td>
            <td>
              <template v-if="el['license_id'] < 500">
                <a href="javascript:void(0)" v-on:click="linfo(el['license_id'])">
                  {{el['count']}}
                </a>
              </template>
              <template v-if="el['license_id'] >= 500">
                <a href="javascript:void(0)" v-on:click="linfoF(el['license_id'])">
                  {{el['count']}}
                </a>
              </template>
            </td>
          </tr>
          </tbody>
        </table>
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
      ldata: Array,
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
        "endpoint",
      ]),
      linfoF: function () {
        // @ts-ignore
        let type = window.performance.getEntriesByType("navigation")[0].type;
        console.log(type);
        let [repoID, groupID] = [null, null];
        let apiData = JSON.parse(JSON.stringify(this.$store.state.common.apiRepos));
        let host = apiData[Object.keys(apiData)[0]]._host;
        if (type === "reload") {
          repoID = apiData[Object.keys(apiData)[0]].repo_id;
          groupID = apiData[Object.keys(apiData)[0]].repo_group_id;
        } else {
          repoID = apiData[Object.keys(apiData)[1]].repo_id;
          groupID = apiData[Object.keys(apiData)[1]].repo_group_id;
        }
        fetch(`${host}/api/unstable/500/False/${groupID}/${repoID}/license-files`)
          .then(res => res.json())
          .then(res => {
            let res_refined: { [index: string]: number } = {};
            for (let i in res) {
              res_refined[Number(i)] = res[i].file_name
            }
            let uriContent = URL.createObjectURL(new Blob([JSON.stringify(res_refined, null, 2)], {type: "text/json;charset=utf-8"}));
            let link = document.createElement("a");
            link.setAttribute("href", uriContent);
            if (type === "reload") {
              link.setAttribute("download", Object.keys(apiData)[0] + ".NOASSERTION.files.json");
            } else {
              link.setAttribute("download", Object.keys(apiData)[1] + ".NOASSERTION.files.json");
            }
            let event = new MouseEvent("click");
            link.dispatchEvent(event);
          });
      },
      linfo: function (license_id) {
        // @ts-ignore
        let type = window.performance.getEntriesByType("navigation")[0].type;
        let [repoID, groupID] = [null, null];
        let apiData = JSON.parse(JSON.stringify(this.$store.state.common.apiRepos));
        let host = apiData[Object.keys(apiData)[0]]._host;
        if (type === "reload") {
          repoID = apiData[Object.keys(apiData)[0]].repo_id;
          groupID = apiData[Object.keys(apiData)[0]].repo_group_id;
        } else {
          repoID = apiData[Object.keys(apiData)[1]].repo_id;
          groupID = apiData[Object.keys(apiData)[1]].repo_group_id;
        }
        console.log("*********************");
        console.log(repoID);
        fetch(`${host}/api/unstable/${license_id}/True/${groupID}/${repoID}/license-files`)
          .then(res => res.json())
          .then(res => {
            let res_refined: { [index: string]: number } = {};
            for (let i in res) {
              res_refined[Number(i)] = res[i].file_name
            }
            let uriContent = URL.createObjectURL(new Blob([JSON.stringify(res_refined, null, 2)], {type: "text/json;charset=utf-8"}));
            let link = document.createElement("a");
            link.setAttribute("href", uriContent);
            if (type === "reload") {
              link.setAttribute("download", Object.keys(apiData)[0] + "." + res[0].short_name + ".files.json");
            } else {
              link.setAttribute("download", Object.keys(apiData)[1] + "." + res[1].short_name + ".files.json");
            }
            let event = new MouseEvent("click");
            link.dispatchEvent(event);
          });
      },
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
          console.log("sbom", tuples, this.base);
          let ref = this.base.url || this.base.repo_name;
          let values: any = [];
          Object.keys(tuples[ref]).forEach((endpoint) => {
            console.log("sbom", ref, endpoint);
            values = tuples[ref][endpoint]
          });
          console.log("sbom loaded", JSON.stringify(values));
          this.values = values;
          this.loaded = true;
          console.log(this.loaded, this.values)

        })
      }
    }
  }
</script>

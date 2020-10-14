<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div class="main-content-container container-fluid px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <span class="text-uppercase page-subtitle">Viewing all</span>
        <div class="title-container">
          <h3 class="page-title">Repo Groups</h3>
        </div>
      </div>
    </div>

    <!-- Default Light Table -->
    <div class="row">
      <div class="col">
        <div class="card card-small mb-4">
          <div class="card-header border-bottom">
            <h6 class="m-0">Currently Stored Groups</h6>
          </div>

          <d-card-body v-if="!loadedGroups">
            <spinner></spinner>
          </d-card-body>

          <div v-if="loadedGroups" class="card-body p-0 pb-3 text-center">
            <table style="table-layout:fixed;" class="table mb-0">
              <thead class="bg-light">
                <tr>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_name')">
                    <div class="row">
                      <div class="col col-9">Name</div>
                      <div
                        class="arrow"
                        v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"
                        v-if="'rg_name' == sortColumn"
                      ></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_description')">
                    <div class="row">
                      <div class="col col-9">Description</div>
                      <div
                        class="arrow"
                        v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"
                        v-if="'rg_description' == sortColumn"
                      ></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_website')">
                    <div class="row">
                      <div class="col col-9">Website</div>
                      <div
                        class="arrow"
                        v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"
                        v-if="'rg_website' == sortColumn"
                      ></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_last_modified')">
                    <div class="row">
                      <div class="col col-9">Last Modified</div>
                      <div
                        class="arrow"
                        v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"
                        v-if="'rg_last_modified' == sortColumn"
                      ></div>
                    </div>
                  </th>
                  <th scope="col" class="border-0" v-on:click="sortTable('rg_type')">
                    <div class="row">
                      <div class="col col-9">Type</div>
                      <div
                        class="arrow"
                        v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"
                        v-if="'rg_type' == sortColumn"
                      ></div>
                    </div>
                  </th>
                  <!-- <th scope="col" class="border-0" v-on:click="sortTable('repo_count')"> 
                    <div class="row">
                      <div class="col col-9">Repo Count</div>
                      <div class="arrow" v-bind:class="ascending ? 'arrow_up' : 'arrow_down'" v-if="'repo_count' == sortColumn"></div>
                    </div>
                  </th>-->
                  <!-- <th scope="col" class="border-0">Options</th> -->
                </tr>
              </thead>
              <tbody>
                <tr v-for="(group, index) in sortedRepoGroups(sortColumn, ascending)">
                  <td>
                    <a href="#" @click="onRepoGroup(group)">{{ group.rg_name }}</a>
                  </td>
                  <td>{{ group.rg_description }}</td>
                  <td>{{ group.rg_website }}</td>
                  <td>{{ group.rg_last_modified }}</td>
                  <td>{{ group.rg_type }}</td>
                  <!-- <td>{{ group.repo_count }}</td> -->
                  <!-- <td>
                    <div class="row">
                      <button :id="'favorite'+index" class="nav-link col col-2" style="margin-left: 2rem; margin-right: 1rem; padding: 0; border: none; background: none;">
                        <i class="material-icons" style="color:#007bff;">star_rate</i>
                        <div class="item-icon-wrapper"></div>
                      </button>
                      <d-tooltip :target="'#favorite'+index"
                        :triggers="['hover']"
                        container=".shards-demo--example--tooltip-01">
                        Consider this repo group as a "favorite" and our workers will regulaly update its metrics' data before others
                      </d-tooltip>
                      <button :id="'add_compare'+index" class="nav-link col col-2" style="padding: 0; border: none;
                      background: none;" v-on:click="addComparedGroup(group)">
                        <i class="material-icons" style="color:#007bff;">library_add</i>
                        <div class="item-icon-wrapper"></div>
                      </button>
                      <d-tooltip :target="'#add_compare'+index"
                        :triggers="['hover']"
                        container=".shards-demo--example--tooltip-01">
                        Add this repo group to your current compared repos
                      </d-tooltip>
                    </div>
                  </td>-->
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.title-container {
  display: flex;
}

.title-container > button {
  background-color: white;
  color: #007BFF;
  border: none;
  box-shadow: 1px 1px 0 4px black;
}
</style>

<script lang="ts">
import Component from "vue-class-component";
import Vue from "vue";
import { mapActions, mapGetters, mapMutations } from "vuex";
import Spinner from "@/components/Spinner.vue";
@Component({
  components: {
    Spinner
  },
  methods: {
    ...mapActions("common", [
      "endpoint", // map `this.endpoint({...})` to `this.$store.dispatch('endpoint', {...})`
      // uses: this.endpoint({endpoints: [], repos (optional): [], repoGroups (optional): []})
      "getRepoRelations",
      "loadRepoGroups",
      "addRepoGroup"
    ]),
    ...mapMutations("common", ["setCompareType"]),
    ...mapActions("compare", ["addComparedGroup", "setBaseGroup"])
  },
  computed: {
    ...mapGetters("common", ["sortedRepoGroups", "repoGroups"])
  }
})
export default class RepoGroups extends Vue {
  colors: string[] = [
    "#343A40",
    "#24a2b7",
    "#159dfb",
    "#FF3647",
    "#4736FF",
    "#3cb44b",
    "#ffe119",
    "#f58231",
    "#911eb4",
    "#42d4f4",
    "#f032e6"
  ];
  testEndpoints: string[] = ["issuesClosed", "codeChangesLines", "issueNew"];
  testTimeframes: string[] = ["past 1 month", "past 3 months", "past 2 weeks"];
  repos: any[] = [];
  repo_relations: any[] = [];
  themes: string[] = ["dark", "info", "royal-blue", "warning"];
  loadedGroups: boolean = false;
  loadedSparks: boolean = false;
  ascending: boolean = true;
  sortColumn: string = "rg_name";

  // declare Vuex action and getter

  getRepoRelations!: any;
  loadRepoGroups!: any;
  repo_groups!: any[];
  sortedRepoGroups!: any[];
  addRepoGroup!: any;
  setBaseGroup!: any;

  // compare module store
  addComparedGroup!: any;

  created() {
    if (!this.loadedGroups) {
      this.loadRepoGroups().then(() => {
        this.loadedGroups = true;
      });
    }
  }

  sortTable(col: string) {
    if (this.sortColumn === col) {
      this.ascending = !this.ascending;
    } else {
      this.ascending = true;
      this.sortColumn = col;
    }
  }

  onRepoGroup(e: any) {
    this.$router.push({
      name: "group_overview",
      params: { group: e.rg_name, repo_group_id: e.repo_group_id }
    });
  }
}
</script>

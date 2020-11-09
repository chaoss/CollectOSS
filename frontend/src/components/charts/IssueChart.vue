<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div class="row section">
    <issue-overview-modal></issue-overview-modal>
    <div class="repo-link-holder issue_overview">
      <div class="issue_overview issue_overview_head">
        <table class="is-responsive issue_overview">
          <thead class="issue_overview issue_overview_head">
          <tr>
            <th v-on:click="sortTable('issue_id')" class="issueChartCellA">ID
              <div class="arrow" v-if="'issue_id' == sortColumn"
                   v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div>
            </th>
            <th v-on:click="sortTable('issue_title')" class="issueChartCellB">Title
              <div class="arrow" v-if="'issue_title' == sortColumn"
                   v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div>
            </th>
            <th v-on:click="sortTable('status')" class="issueChartCellA">Status
              <div class="arrow" v-if="'status' == sortColumn"
                   v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div>
            </th>
            <th v-on:click="sortTable('count')" class="issueChartCellA">Events Count
              <div class="arrow" v-if="'count' == sortColumn"
                   v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div>
            </th>
            <th v-on:click="sortTable('date')" class="issueChartCellC">Open Date
              <div class="arrow" v-if="'last_event_date' == sortColumn"
                   v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div>
            </th>
            <th v-on:click="sortTable('last_event_date')" class="issueChartCellC">Last Event Date
              <div class="arrow" v-if="'last_event_date' == sortColumn"
                   v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div>
            </th>
            <th v-on:click="sortTable('open_day')" class="issueChartCellA">Open Day
              <div class="arrow" v-if="'open_day' == sortColumn"
                   v-bind:class="ascending ? 'arrow_up' : 'arrow_down'"></div>
            </th>
          </tr>
          </thead>
        </table>
      </div>
      <div class="issue_overview issue_overview_scroll">
        <table>
          <tbody class="issue_overview">
          <tr v-for="issue in issues">
            <td class="issueChartCellA">{{ issue.issue_id }}</td>
            <td class="issueChartCellB"><a href="#" @click.prevent="toggleModal(issue)">{{ issue.issue_title }}</a></td>
            <td class="issueChartCellA">{{ issue.status }}</td>
            <td class="issueChartCellA">{{ issue.count }}</td>
            <td class="issueChartCellC">{{ issue.date }}</td>
            <td class="issueChartCellC">{{ issue.last_event_date }}</td>
            <td class="issueChartCellA">{{ issue.open_day }}</td>
          </tr>
          </tbody>
        </table>
      </div>
      <p> {{ chart }} </p>
    </div>
  </div>
</template>

<script>
  import IssueOverviewModal from '../IssusOverViewModal.vue'

  export default {
    components: {
      IssueOverviewModal
    },
    props: ['source', 'citeUrl', 'citeText', 'title', 'data'],
    data() {
      return {
        issues: [],
        isModalVisible: false
      }
    },
    computed: {
      repo() {
        return this.$store.state.baseRepo
      },
      gitRepo() {
        return this.$store.state.gitRepo
      },
      period() {
        return this.$store.state.trailingAverage
      },
      earliest() {
        return this.$store.state.startDate
      },
      latest() {
        return this.$store.state.endDate
      },
      compare() {
        return this.$store.state.compare
      },
      comparedRepos() {
        return this.$store.state.comparedRepos
      },
      rawWeekly() {
        return this.$store.state.rawWeekly
      },
      showArea() {
        return this.$store.state.showArea
      },
      showTooltip() {
        return this.$store.state.showTooltip
      },
      showDetail() {
        return this.$store.state.showDetail
      },
      chart() {
        let repo = null;
        if (this.repo) {
          if (window.AugurRepos[this.repo]) {
            repo = window.AugurRepos[this.repo]
          } else {
            let repo = window.AugurAPI.Repo({"gitURL": this.gitRepo});
            window.AugurRepos[repo.toString] = repo
          }
        } else {
          repo = window.AugurAPI.Repo({gitURL: this.gitRepo});
          window.AugurRepos[repo.toString()] = repo
        }
        let processData = (data) => {
          this.issues = data
        };
        if (this.data) {
          processData(this.data[repo.toString()]["getIssues"])
        } else {
          repo.getIssues().then((lists) => {
            processData(lists)
          })
        }
      }
    },
    methods: {
      sortTable(col) {
        if (this.sortColumn === col) {
          this.ascending = !this.ascending;
        } else {
          this.ascending = true;
          this.sortColumn = col;
        }
        let ascending = this.ascending;
        this.issues.sort(function (a, b) {
          if (a[col] > b[col]) {
            return ascending ? 1 : -1
          } else if (a[col] < b[col]) {
            return ascending ? -1 : 1
          }
          return 0;
        })
      },
      toggleModal(e) {
        window.AugurApp.$emit('toggleModal', e);
      }
    }
  }
</script>

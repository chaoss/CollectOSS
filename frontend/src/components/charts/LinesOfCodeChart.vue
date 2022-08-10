<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-card-body class="linesofCodeChart">
    <table class="lines-of-code-table">
      <thead>
        <tr>
          <th>Author</th>
          <th
            v-if="!setYear"
            v-for="year in years"
            v-on:click="setYear = year"
            class="clickable-header"
          >{{ year }}</th>
          <th v-if="setYear" v-for="month in monthNames">{{ month }}</th>
          <th v-if="!setYear">Total all time</th>
          <th v-if="setYear" v-on:click="setYear = 0">{{ setYear }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="contributor in contributors.slice(0, 10)">
          <td>{{ contributor.cmt_author_email }}</td>
          <td
            v-if="!setYear"
            v-for="year in years"
          >{{ (contributor[year]) ? contributor[year].additions || 0 : 0}}</td>
          <td
            v-if="setYear"
            v-for="month in monthDecimals"
          >{{ (contributor[setYear + '-' + month]) ? contributor[setYear + '-' + month].additions || 0 : 0 }}</td>
          <td v-if="!setYear">{{ contributor.additions }}</td>
          <td v-if="setYear">{{ (contributor[setYear]) ? contributor[setYear].additions || 0 : 0}}</td>
        </tr>
      </tbody>
    </table>
    <br />
    <h3>Lines of code added by the top 5 organizations</h3>
    <table class="lines-of-code-table">
      <thead>
        <tr>
          <th>Author</th>
          <th
            v-if="!setYear"
            v-for="year in years"
            v-on:click="setYear = year"
            class="clickable-header"
          >{{ year }}</th>
          <th v-if="setYear" v-for="month in monthNames">{{ month }}</th>
          <th v-if="!setYear">Total all time</th>
          <th v-if="setYear" v-on:click="setYear = year" class="clickable-header">{{ setYear }}</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="organization in organizations.slice(0, 10)">
          <td>{{ organization.name }}</td>
          <td
            v-if="!setYear"
            v-for="year in years"
          >{{ (organization[year]) ? organization[year].additions || 0 : 0}}</td>
          <td
            v-if="setYear"
            v-for="month in monthDecimals"
          >{{ (organization[setYear + '-' + month]) ? organization[setYear + '-' + month].additions || 0 : 0}}</td>
          <td v-if="!setYear">{{ organization.additions }}</td>
          <td v-if="setYear">{{ (organization[setYear]) ? organization[setYear].additions || 0 : 0}}</td>
        </tr>
      </tbody>
    </table>
    <p>{{ chart }}</p>
  </d-card-body>
</template>


<script>
export default {
  props: ["source", "citeUrl", "citeText", "title", "data"],
  data() {
    // console.log('yearDifference: ' + yearDifference);
    let years = [];
    // for (let i = 14; i >= 0; i--) {
    //   years.push(new Date().getFullYear() - i);
    // }
    let monthNames = [
      "Jan",
      "Feb",
      "Mar",
      "Apr",
      "May",
      "Jun",
      "Jul",
      "Aug",
      "Sep",
      "Oct",
      "Nov",
      "Dec"
    ];
    let monthDecimals = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    return {
      contributors: [],
      organizations: [],
      view: "year",
      monthNames: monthNames,
      monthDecimals: monthDecimals,
      years: [],
      setYear: 0
    };
  },
  mounted() {
    // calculate the minimum year and maximum year of all commits
    let minDate = Number(new Date().getFullYear());
    let maxDate = 0;

    this.data.forEach(commit => {
      if (Number(commit.cmt_author_date.getFullYear()) < minDate) {
        minDate = commit.cmt_author_date.getFullYear();
      }
      if (Number(commit.cmt_author_date.getFullYear()) > maxDate) {
        maxDate = commit.cmt_author_date.getFullYear();
      }
    });

    let yearDifference = maxDate - minDate;

    // push years based on these minimums and maximums
    for (let i = minDate; i <= maxDate; i++) {
      this.years.push(i);
    }
  },
  computed: {
    repo() {
      return this.$store.state.baseRepo;
    },
    gitRepo() {
      return this.$store.state.gitRepo;
    },
    chart() {
      let repo = null;

      let contributors = {};
      let organizations = {};

      let addChanges = (dest, src) => {
        if (dest && src) {
          if (typeof dest !== "object") {
            dest["additions"] = 0;
            dest["deletions"] = 0;
          }
          dest["additions"] += src["additions"] || 0;
          dest["deletions"] += src["deletions"] || 0;
        }
      };

      let group = (obj, name, change, filter) => {
        if (filter(change)) {
          let year = new Date(change.cmt_author_date).getFullYear();
          let month = new Date(change.cmt_author_date).getMonth();
          obj[change[name]] = obj[change[name]] || {
            additions: 0,
            deletions: 0
          };
          addChanges(obj[change[name]], change);
          obj[change[name]][year] = obj[change[name]][year] || {
            additions: 0,
            deletions: 0
          };
          addChanges(obj[change[name]][year], change);
          obj[change[name]][year + "-" + month] = obj[change[name]][
            year + "-" + month
          ] || { additions: 0, deletions: 0 };
          addChanges(obj[change[name]][year + "-" + month], change);
        }
      };

      let flattenAndSort = (obj, keyName, sortField) => {
        return Object.keys(obj)
          .map(key => {
            let d = obj[key];
            d[keyName] = key;
            return d;
          })
          .sort((a, b) => {
            return b[sortField] - a[sortField];
          });
      };

      let filterDates = change => {
        return new Date(change.cmt_author_date).getFullYear() > this.years[0];
      };

      let processData = changes => {
        changes.forEach(change => {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, "cmt_author_email", change, filterDates);
            if (change.author_affiliation !== "Unknown") {
              group(organizations, "affiliation", change, filterDates);
            }
          }
        });
        console.log(contributors);

        this.contributors = flattenAndSort(
          contributors,
          "cmt_author_email",
          "additions"
        );
        this.organizations = flattenAndSort(organizations, "name", "additions");
      };

      if (this.data) {
        console.log(this.data);
        processData(this.data);
      } else {
        repo.changesByAuthor().then(data => {
          processData(data);
        });
      }
    }
  }
};
</script>

<style>
.card-body {
  overflow: scroll;
}
</style>
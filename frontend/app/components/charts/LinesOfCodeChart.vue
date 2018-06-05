<template>
  <div ref="holder">
      <h3>Lines of code added by the top 10 authors</h3>
      <table>
        <thead>
          <tr>
            <td>Author</td>
            <td v-for="year in years">{{ year }}</td>
            <td>Total all time</td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contributor in contributors.slice(0, 10)">
            <td>{{ contributor.email }}</td>
            <td v-for="year in years">{{ (contributor[year]) ? contributor[year].additions || 0 : 0}}</td>
            <td>{{ contributor.additions }}</td>
          </tr>
        </tbody>
      </table>
      <br>
      <h3>Lines of code added by the top 5 organizations</h3>
      <table>
        <thead>
          <tr>
            <td>Author</td>
            <td v-for="year in years">{{ year }}</td>
            <td>Total all time</td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="organization in organizations.slice(0, 10)">
            <td>{{ organization.name }}</td>
            <td v-for="year in years">{{ (organization[year]) ? organization[year].additions || 0 : 0}}</td>
            <td>{{ organization.additions }}</td>
          </tr>
        </tbody>
      </table>
      <p> {{ chart }} </p>
  </div>
</template>


<script>
export default {
  props: ['source', 'citeUrl', 'citeText', 'title'],
  data() {
    let years = []
    for (let i = 4; i >= 0; i--) {
      years.push((new Date()).getFullYear() - i)
    }
    return {
      contributors: [],
      organizations: [],
      years: years
    }
  },
  computed: {
    repo() {
      return this.$store.state.gitRepo
    },
    chart() {
      let repo = window.AugurAPI.Repo({ gitURL: this.repo })
      let contributors = {}
      let organizations = {}

      let addChanges = (dest, src) => {
        if (dest && src) {
          if (typeof dest !== 'object') {
            dest['additions'] = 0
            dest['deletions'] = 0
          }
          dest['additions'] += (src['additions'] || 0)
          dest['deletions'] += (src['deletions'] || 0)
        }
      }

      let group = (obj, name, change) => {
        let year = (new Date(change.author_date)).getFullYear()
        obj[change[name]] = obj[change[name]] || { additions: 0, deletions: 0 }
        addChanges(obj[change[name]], change)
        obj[change[name]][year] = obj[change[name]][year] || { additions: 0, deletions: 0 }
        addChanges(obj[change[name]][year], change)
      }

      let flattenAndSort = (obj, keyName, sortField) => {
        return Object.keys(obj)
            .map((key) => {
              let d = obj[key]
              d[keyName] = key
              return d
            })
            .sort((a, b) => {
              return b[sortField] - a[sortField]
            })
      }

      repo.linesChangedMinusWhitespace().then((changes) => {
        changes.forEach((change) => {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            group(contributors, 'author_email', change)
            if (change.author_affiliation !== 'Unknown') {
              group(organizations, 'author_affiliation', change)
            }
          }
        })
        
        this.contributors = flattenAndSort(contributors, 'email', 'additions')
        this.organizations = flattenAndSort(organizations, 'name', 'additions')
            

        console.log(this.contributors)
      })
    }
  }
}

</script>

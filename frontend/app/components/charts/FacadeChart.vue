<template>
  <div ref="holder">
    <div class="textchart">
      <h3>Lines of code added by the top 10 authors</h3>
      <table>
        <thead>
          <tr>
            <td>Author</td>
            <td v-for="year in years">{{ year }}</td>
            <td>Total</td>
          </tr>
        </thead>
        <tbody>
          <tr v-for="contributor in contributors">
            <td>{{ contributor.email }}</td>
            <td v-for="year in years">{{ (contributor[year]) ? contributor[year].additions || 0 : 0}}</td>
            <td>{{ contributor.additions }}</td>
          </tr>
        </tbody>
      </table>
      <p> {{ chart }} </p>
    </div>
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
      years: years
    }
  },
  computed: {
    repo() {
      return this.$store.state.gitRepo
    },
    chart() {
      let repo = window.AugurAPI.Repo({ gitURL: this.repo })

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

      repo.linesChangedMinusWhitespace().then((changes) => {
        let contributors = {}
        changes.forEach((change) => {
          if (isFinite(change.additions) && isFinite(change.deletions)) {
            contributors[change.author_email] = contributors[change.author_email] || { additions: 0, deletions: 0 }
            addChanges(contributors[change.author_email], change)
            let year = (new Date(change.author_date)).getFullYear()
            contributors[change.author_email][year] = contributors[change.author_email][year] || { additions: 0, deletions: 0 }
            addChanges(contributors[change.author_email][year], change) 
          }
        })
        
        this.contributors = 
            Object.keys(contributors)
            .map((key) => {
              let obj = contributors[key]
              obj['email'] = key
              return obj
            })
            .sort((a, b) => {
              return b.additions - a.additions
            })
            .slice(0, 10)

        console.log(this.contributors)
      })
    }
  }
}

</script>

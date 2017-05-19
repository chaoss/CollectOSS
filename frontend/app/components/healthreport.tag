<healthreport>

<div class="container">

  <section>
    <div class="row">
      <div class="nine columns"><h1 id="repo-label">{owner} / {repo}</h1></div>
    </div>
  </section>

  <section>

    <div class="row">
      <div class="twelve columns">
        <h2>Response to Issues</h2>
        <issueshistogram></issueshistogram>
      </div>
    </div>

    <div class="spacer"></div>

    <div class="row">
      <div class="twelve columns">
        <h2>Contributions</h2>
        <contributions></contributions>
      </div>
    </div>

  </section>
</div>

<script>

  this.owner = this.opts.owner
  this.repo = this.opts.repo

  var ghdata = require('../lib/ghdata-api-client')
  var api = new ghdata.GHDataAPIClient(undefined, this.owner, this.repo)

  this.on('mount', function () {
    require('./contributions.tag');
    require('./issueshistogram.tag');
    riot.mount('issueshistogram', {api: api})
    riot.mount('contributions', {api: api})
  })

</script>

</healthreport>
### Step 1. Write the algorithim that calculates the metrics.

First, you need to determine the best place to put your metric. GHData is broken up into classes based on the source of the data, so you'll want to put your code in the class that is appropiate for your metrics. For instance, if we wanted to develop a new metric that measures how old a repo is, we would put that function in [ghtorrent.py](https://github.com/OSSHealth/ghdata/blob/master/ghdata/ghtorrent.py) since it will get its data from GHTorrent:

```python
class GHTorrent(object):

    # ..all the existing code...

    def repo_age(self, repoid):
        projectDaysSQL = s.sql.text("""
            SELECT DATEDIFF(NOW(), projects.created_at) as "days_since_creation"
            FROM projects
            WHERE projects.id = :repoid
        """)
        return pd.read_sql(projectDaysSQL, self.db, params={"repoid": str(repoid)})
```

### Step 2. Add the route to the Flask server

After creating the new metric, you must make [server.py](https://github.com/OSSHealth/ghdata/blob/master/ghdata/server.py) aware of it. Add the route:

```python
# ...all the other app.route functions...

app.route('/{}/<owner>/<repo>/age'.format(GHDATA_API_VERSION))(flaskify_ghtorrent(ghtorrent, ghtorrent.repo_age))
#                             ^ what you want the endpoint to be                                       ^ your function  
```

### Step 3. Create/use an appropiate riot tag for the metric

In [frontend/app/components](https://github.com/OSSHealth/ghdata/tree/dev/frontend/app/components) there exist a number of riot tags suited for different metrics. Each metric tag must be mounted by the `<healthreport>` tag, because the health report tag passes the repo/owner information to the metric tags.

To create a new tag, create a file with the name of the tag. For instance, if you were creating a tag for the repo age, you might create a file called `repoage.tag` in [frontend/app/components](https://github.com/OSSHealth/ghdata/tree/dev/frontend/app/components).

Then you would write the riot tag to display the metric. Currently, we are using [echarts](https://ecomfe.github.io/echarts-examples/public/index.html) to render charts. See [contributions.tag](https://github.com/OSSHealth/ghdata/tree/dev/frontend/app/components/contributions.tag) as an example. A chart is probably not the most appropiate way to display the age of a repo, so we'll just use a div.

```jsx
<repoage>
<p class="repo-age">This repository is { repoAge } days old.</p>
<script>
    this.on('mount', () => {
        this.opts.api.get('age').then((ageObject) => {
            this.repoAge = ageObject['days_since_creation']
        })
    })
</script>
</repoage>
```

### Step 4. Add the tag to the page

Add your tag to somewhere in [healthreport.tag](https://github.com/OSSHealth/ghdata/tree/dev/frontend/app/components/heathreport.tag)

```jsx
<repoage></repoage>
```

and mount it in the script

```js
require('./repoage.tag');
riot.mount('repoage', {api: api})
```

The metric should be fully integrated into GHData. To install your updated version of GHData, run `pip install --upgrade .` in the root of your repo.

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

### Step 3. Add your endpoint to the GHData API Client

Once your route is avaliable as an endpoint, you'll need to add it to [ghdata-api-client.js](https://github.com/OSSHealth/ghdata/blob/master/ghdata/static/scripts/ghdata-api-client.js) to make it accessible from that JavaScript library:

```js
GHDataAPIClient.prototype.age = function (params) {
  return this.get('age', params);
};
```

### Step 4. Write the UI

In [health-report.js](https://github.com/OSSHealth/ghdata/blob/master/ghdata/static/scripts/health-report.js) you'll now be able to call `this.api.age()` while in the buildReport function. [ghdata-api-client.js](https://github.com/OSSHealth/ghdata/blob/master/ghdata/static/scripts/ghdata-api-client.js) returns a Promise, so you'll need to write your code in context of the fufillment of that promise:

```js
this.api.age().then(function (age) {
  console.log(age);
})
```

If you are creating a metric that is a timeseries (like the ones that exist now), you'll need to add a `<div>` to the html:

```html
<div class="four columns" id="your-timeseries-name-over-time"></div>
```

Then write the new method in [health-report.js](https://github.com/OSSHealth/ghdata/blob/master/ghdata/static/scripts/health-report.js):

```js
this.api.yourMetricName().then(function (yourMetric) {
MG.data_graphic({
    title: "Stars/Week",
    data: MG.convert.date(yourMetric, 'date', '%Y-%m-%dT%H:%M:%S.%LZ'),
    chart_type: 'point',
    least_squares: true,
    full_width: true,
    height: 300,
    color_range: ['#aaa'],
    x_accessor: 'date',
    y_accessor: 'watchers',
    target: '#your-timeseries-name-over-time'
});
```




The metric should be fully integrated into GHData. To install your updated version of GHData, run `pip3 install --upgrade .` in the root of your repo.

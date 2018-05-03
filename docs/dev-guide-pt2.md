# Developer Guide Part 2 - The Frontend

## Structure
GHData uses Vue.js, MetricsGraphics, Kube for its frontend. The frontend is stored in the `frontend` directory, but the parts that are relevant to adding new metrics are in the `frontend/app/` directory, which contains the following parts:
* `frontend/app/GHDataAPI.js` which interfaces with the backend
* `frontend/app/GHDataStats.js` which performs statistical operations on the data
* `frontend/app/GHData.js` which renders the page
* `frontend/app/assets/` which contains the assets, such as images, for the frontend
* `frontend/app/include/` which contains the Kube and MetricsGraphics resources
* `frontend/styles/` which contains the stylesheet for GHData
* `frontend/components/` which contains the Vue.js components
  * `frontend/components/charts/` contains the different chart templetes
  * `frontend/components/BaseRepoActivityCard.vue` contains the repo activity time series charts

## How to add a new timeseries metric

### Adding an endpoint

In `frontend/app/GHDataAPI.js`, add an attribute to the repo class that holds a times eries object at the end of the file like this 
```javascript
repo.<endpointName> = Timeseries('endpoint_name')
```
So if your endpoint name is `foo_bar` then the attribute would be
```javascript
repo.<fooBar> = Timeseries('foo_bar')
```

### Adding a chart
In `frontend/app/components/BaseRepoActivityCard.vue`, in the template in the section tag, add a div like this
```html
    <div class="row">
      <div class="col col-'width'>
        <line-chart source="attributeName" 
                    title="Chart title" 
                    cite-url="Optional link to explanation"
                    cite-text="Optional link title">
        </line-chart>
      </div>
```
The recommended width is 6 for half width and 12 for full width. So if I wanted to add the `foo_bar`chart, it would look like this
```html
    <div class="row">
      <div class="col col-12>
        <line-chart source="fooBar" 
                    title="Foo Bar" 
                    cite-url="https://foobar.com"
                    cite-text="Link to foo bar explination">
        </line-chart>
      </div>
```
### Adding Comparison Functionality
In `frontend/app/components/ComparedRepoActivityCard.vue` in the template in the section tag, add a div like this
```html
    <div class="row">
      <div class="col col-'width'>
        <line-chart source="attributeName" 
                    title="Chart title" 
                    cite-url="Optional link to explanation"
                    cite-text="Optional link title"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>
```
The recommended width is 6 for half width and 12 for full width. So if I wanted to add the `foo_bar`chart, it would look like this
```html
    <div class="row">
      <div class="col col-12>
        <line-chart source="fooBar" 
                    title="Foo Bar" 
                    cite-url="https://foobar.com"
                    cite-text="Link to foo bar explination"
                    v-bind:compared-to="comparedTo">
        </line-chart>
      </div>
```
## How to add a new nontimeseries metric

### Adding an endpoint

In `frontend/app/GHDataAPI.js`, add an attribute to the repo class that holds an endpoint object at the end of the file like this
```javascript
repo.<endpointName> = Endpoint('endpoint_name')
```
So if your endpoint name is `foo_bar` then the attribute would be
```javascript
repo.<fooBar> = Endpoint('foo_bar')
```

### Adding a chart
In the `frontend/app/components/charts` directory define a chart for the metric

In `frontend/app/components/BaseRepoActivityCard.vue` or `frontend/app/components/BaseRepoEcosystemCard.vue` import the chart at the bottom and export it

In the same file, in the template in the section tag, add a div like this
```html
    <div class="row">
      <div class="col col-'width'">
        <chart-type source="attributeName"
                    title="Chart title"
                    cite-url="Optional link to explanation"
                    cite-text="Optional link title">
        </chart-type>
      </div>
...
import ChartType from './charts/ChartType'

module.exports = {
  components: {
    ChartType
  }
};
```
The recommended width is 6 for half width and 12 for full width. So if I wanted to add the `foo_bar` chart, it would look like this
```html
    <div class="row">
      <div class="col col-12">
        <foo-bar source="fooBar"
                    title="Foo Bar"
                    cite-url="https://foobar.com"
                    cite-text="Link to foo bar explanation">
        </foo-bar>
      </div>
...
import FooBar from './charts/FooBar'

module.exports = {
  components: {
    FooBar
  }
};
```

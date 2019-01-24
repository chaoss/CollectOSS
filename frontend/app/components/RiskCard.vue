\\<template>
  <section>
    <h1>Risk</h1>
    <div style="display: inline-block;">
      <h2 id="base" style="display: inline-block; color: black !important">{{ $store.state.baseRepo }}</h2>
      <h2 style="display: inline-block;" class="repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: 
</h2>
      <h2 style="display: inline-block;" v-for="(repo, index) in $store.state.comparedRepos">
        <span id="compared" v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span>
      </h2>
    </div>
    <script type="application/javascript">
        var request = new XMLHttpRequest;
        async function loader() {
            const augURL = 'https://github.com/' + document.getElementById("base").innerHTML;
            console.log(augURL);
            request.open('GET', 'https://bestpractices.coreinfrastructure.org/projects.json?pq=' + augURL, true);
            request.onload = function () {
                var data = JSON.parse(this.response)[0];
                console.log('CII NAME: ' + data.name);
                console.log(data);
                badgeURL = 'https://bestpractices.coreinfrastructure.org/projects/' + data.id + '/badge';
                console.log(badgeURL);
                document.getElementById("CIIbadge").src = badgeURL;
                if (data.badge_percentage_0 < 100) {
                document.getElementById("CII").innerHTML = data.name + ' is currently not passing CII Best Practices.';
                }
                else if (data.badge_percentage_1 < 100) {
                document.getElementById("CII").innerHTML = data.name + ' is currently passing CII Best Practices.';
                }
                else if (data.badge_percentage_2 < 100) {
                document.getElementById("CII").innerHTML = data.name + ' is currently passing CII Best Practices. This project has a siver status.';
                }
                else if (data.badge_percentage_2 == 100) {
                document.getElementById("CII").innerHTML = data.name + ' is currently passing CII Best Practices. <br>' + data.name + ' maintains a gold status.';
                }
            }
        }
        loader();
        request.send();
    </script>
    <h2 class="col" style="margin-bottom:20px">CII Best Practices</h2>
    <div class="row">
        <div id="CIIbp" class="col-6">
            <div size="total">
            <img id="CIIbadge">
            <p id="CII"></p>
            </div>
        </div>
        <div id="CIIbp" class="col-6">
            <div size="total">
            <img id="CIIbadge2">
            <p id="CII"></p>
            </div>
        </div>
      </div>
    </div>
  </section> 
</template> 

w<script>
import DynamicLineChart from './charts/DynamicLineChart'
import BubbleChart from './charts/BubbleChart'
import StackedBarChart from './charts/StackedBarChart'
module.exports = {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
    }
  },
  components: {
    DynamicLineChart,
    BubbleChart,
    StackedBarChart
  }
}
</script>

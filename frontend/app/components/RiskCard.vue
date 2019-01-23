\\<template>
  <section>
    <h1>Risk</h1>
    <div style="display: inline-block;">
      <h2 id="base" style="display: inline-block; color: black !important">{{ $store.state.baseRepo }}</h2>
      <h2 style="display: inline-block;" class="repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 style="display: inline-block;" v-for="(repo, index) in $store.state.comparedRepos">
        <span v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span> 
      </h2>
    </div>
      <div class="row">
        <script type="application/javascript">
        var request = new XMLHttpRequest;
        async function loader() {
            const augURL = 'https://github.com/' + document.getElementById("base").innerHTML;
            console.log(augURL);
            request.open('GET', 'https://bestpractices.coreinfrastructure.org/projects.json?pq=' + augURL, true);
            request.onload = function () {
                var data = JSON.parse(this.response)[0];
                document.getElementById("CIIName").innerHTML = 'NAME: ' + data.name;
                console.log(data);
                if (data.badge_percentage_0 < 100) {
                document.getElementById("CII").innerHTML = 'No badges! <br>%' + data.badge_percentage_0 + ' to the passing badge!';
                }
                else if (data.badge_percentage_1 < 100) {
                document.getElementById("CII").innerHTML = 'Passing badge got! <br>%' + data.badge_percentage_1 + ' to the silver badge!';
                }
                else if (data.badge_percentage_2 < 100) {
                document.getElementById("CII").innerHTML = 'Siver badge got! <br>%' + data.badge_percentage_2 + ' to the gold badge!';
                }
                else if (data.badge_percentage_2 == 100) {
                document.getElementById("CII").innerHTML = 'Gold badge got! ';
                }
            }
        }
        loader();
        request.send();
        </script>
        <div id="CIIbox">
            <h2 id="CIIName"></h2>
            <p id="CII"></p>
        </div>
      </div>
    </div>

  </section>
</template>

<script>

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

<!-- #SPDX-License-Identifier: MIT -->
<template>
  <section>
    <h1>Risk</h1>
    <div class="riskCard">
      <h2 id="base" class="riskCardHeader">{{ $store.state.baseRepo }}</h2>
      <h2 class="riskCard repolisting" v-if="$store.state.comparedRepos.length > 0"> compared to: </h2>
      <h2 class="riskCard" v-for="(repo, index) in $store.state.comparedRepos">
        <span id="compared" v-bind:style="{ 'color': colors[index] }" class="repolisting"> {{ repo }} </span>
      </h2>
    </div>
    <h2 class="col riskCardHeader2" >CII Best Practices</h2>
    <button id="ciiBtn" class="riskCardButton">Retrieve CII information</button>
    <div id="overcii" class="riskCardDiv1">
        <img class="col riskCardDiv2" width="200px" height="200px"
        src="https://i.ibb.co/n8f7NjX/CIITPARENT.png"
        href="https://bestpractices.coreinfrastructure.org/en">
        <br>
        <div id="CIIbp" class="riskCardDiv3 col-6">
            <div size="total">
            <img id="CIIbadge" class="riskCardImg">
            <br>
            <h2 id="CII"></h2>
            </div>
        </div>
    </div>
  </section>
</template>
<script>
window.onload = function() {
var ciiStuff = document.getElementById("ciiBtn")
if(ciiStuff){
ciiStuff.addEventListener("click", function(){
    document.getElementById("overcii").style.display = "block"
    document.getElementById("overcii").class = "row"
    document.getElementById("ciiBtn").style.visibility = "hidden";
        var request = new XMLHttpRequest();
        function loader() {
            const basestr = document.getElementById("base").innerHTML;
            const augURL = 'https://github.com/' + basestr;
            request.open('GET', 'https://bestpractices.coreinfrastructure.org/projects.json?pq=' + augURL, true);
            request.onload = function () {
                var data = JSON.parse(this.response)[0];
                if (data != undefined) {
                    //console.log('CII NAME: ' + data.name);
                    //console.log(data);
                    var badgeURL = 'https://bestpractices.coreinfrastructure.org/projects/' + data.id + '/badge';
                    //console.log(badgeURL);
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
                } else {
                    document.getElementById("CII").innerHTML = 'No best practice data for this repository.';
                }
            };
    }
    loader();
    request.send();
});
}
}
export default {
  data() {
    return {
      colors: ["#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"]
    }
  },
  components: {
    //RiskChart
  }
}
</script>

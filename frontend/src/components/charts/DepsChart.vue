<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-card-body class="depsChart">
    <table class="deps-table">
      <thead>
        <tr>
          <th>Library Name</th>
          <th>   ---   </th> <!-- dummy row until styling applied to give row spacing -->
          <th>Files Used</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="lib in libraries">
          <td>{{ lib.name }}</td>
          <td>{{ lib.count }}</td>
        </tr>
      </tbody>
    </table>
  </d-card-body>
</template>


<script>
export default {
  props: ["source", "citeUrl", "citeText", "title", "data"],
  data() {
    return {
      libraries: []
    };
  },
  mounted() {
  	console.log("stuart " + this.source);
  	console.log("stuart " + this.data);
  	//this is test code to make sure the card works
  	this.libraries = [];
  	for(let i = 0; i < 10; i += 2) {
  		let x = new Object();
  		x.name = i;
  		x.count = i+1;
  		this.libraries.push(x);
  	}
  	console.log("stuart " + this.libraries);
  }
};
</script>

<style>
.card-body {
  overflow: scroll;
}
</style>

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
    <p>{{ chart }}</p>
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
  computed: {
	  chart() {
	  	//this is test code to make sure the card works
	  	this.libraries = this.data;
	  	console.log("stuart", this, this.data);
	  }
  }
};
</script>

<style>
.card-body {
  overflow: scroll;
}
</style>

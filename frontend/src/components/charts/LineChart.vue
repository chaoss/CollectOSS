<!-- <template>
	<div ref="holder" style="">
	    <div class="chart">
	      	<vega-lite :spec="spec" :data="data"></vega-lite>
	      	<p> {{ chart }} </p>
	    </div>
  	</div>
</template>

<script lang="ts">
import Vue from 'vue'
import Component from 'vue-class-component'

@Component({
  props: {
  	data: Array<any>,
  	description: String,
  	field: String
  },
  components: {
  	//n/a
  }
})
export default class LineChart extends Vue {

	// computed
	get spec () {
		let spec = {
			"$schema": "https://vega.github.io/schema/vega-lite/v3.json",
			"description": this.description,
			"mark": "line",
			"encoding": {
				"x": {"field": "date", "type": "temporal"},
				"y": {"field": this.field, "type": "quantitative"}
			}
		}

		return spec
	}
}
</script> -->
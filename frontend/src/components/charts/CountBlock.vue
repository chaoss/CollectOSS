<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-card>
    <d-card-body :title="title" class="text-center">
      <spinner v-if="!loaded"></spinner>
      <span v-if="loaded" class="countBlockSpan">{{ count }}</span>
    </d-card-body>
  </d-card>
</template>

<script lang="ts">
import { Options, Vue } from "vue-property-decorator";
import { mapActions, mapGetters } from "vuex";
import Spinner from "../../components/Spinner.vue";

class Props {
  title: String;
  data: Object;
  source: String;
  field: String;
}

@Options({
  components: {
    Spinner,
  },
  computed: {
    ...mapGetters("compare", ["comparedRepos", "base"]),
  },
  methods: {
    ...mapActions("common", ["endpoint"]),
  },
})
export default class CountBlock extends Vue.with(Props) {
  loaded: boolean = false;
  count: any[] = [];
  base!: any;
  comparedRepos!: any;
  endpoint!: any;

  created() {
    if (this.data) {
      this.loaded = true;
      this.count = this.data[this.source][0][this.field];
    } else {
      this.endpoint({ endpoints: [this.source], repos: [this.base] }).then(
        (tuples: any) => {
          let ref = this.base.url || this.base.repo_name;
          let values: any = [];
          Object.keys(tuples[ref]).forEach((endpoint) => {
            values = tuples[ref][endpoint];
          });
          this.count = values[0][this.field];
          console.log("countblock", values, this.count);
          this.loaded = true;
        }
      );
    }
  }
}
</script>

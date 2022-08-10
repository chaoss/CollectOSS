<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div class="main-navbar__search w-100 d-none d-md-flex d-lg-flex navbarSearchDiv" >
    <!-- <d-form class="main-navbar__search w-100 d-none d-md-flex d-lg-flex" style="margin-bottom: 0 !important"> -->
        <d-input-group class="ml-3" seamless>
            <d-input-group-text slot="prepend">
                <i class="material-icons">search</i>
            </d-input-group-text>
            <!-- <input type="text" class="search reposearch" name="headersearch" placeholder="GitHub URL" @change="onRepo"> -->
            <d-input class="navbar-search navbarSearchInput" @change="onRepo" placeholder="Search for one of your repos ( *repo group name*/*repo name* )" />
        </d-input-group>
    <!-- </d-form> -->
  </div>
</template>

<script lang="ts">
import { mapActions, mapGetters, mapMutations } from "vuex";
import Component from 'vue-class-component';
import Vue from 'vue';
@Component({
  methods: {
    ...mapActions('common',[
      'retrieveRepoIds',
    ]),
    ...mapActions('compare',[
      'setBaseRepo',
      'setBaseGroup',
    ])
  },
  computed: {
    ...mapGetters('common', [
      'AugurAPI',
    ]),
  },
  components: {
  }
})
export default class Search extends Vue {
  //getters
  AugurAPI!:any
  //actions
  retrieveRepoIds!:any
  setBaseRepo!:any
  setBaseGroup!:any
  onRepo (e:any) {
    let group = e.split('/').length > 1 ? e.split('/')[0] : null
    let repo = e.split('/').length > 1 ? e.split('/')[1] : e.split('/')[0]
    this.retrieveRepoIds({
      repo: repo,
      rg_name: group,
    }).then((ids: any) => {
      // this.setBaseRepo({
      //   rg_name: group,
      //   repo_name: repo,
      //   repo_group_id: ids.repo_group_id,
      //   repo_id: ids.repo_id,
      // }).then((data: any) => {
      //   this.setBaseGroup({
      //     rg_name: group,
      //     repo_name: repo,
      //     repo_group_id: ids.repo_group_id,
      //     repo_id: ids.repo_id,
      //   })
      // })
      this.$router.push({
        name: 'repo_overview',
        params: {'group': ids.rg_name, 'repo': repo, 'repo_group_id': ids.repo_group_id, 'repo_id': ids.repo_id}
      })
    })
  }
};
</script>
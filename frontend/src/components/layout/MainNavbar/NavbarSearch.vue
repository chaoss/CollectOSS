<template>
    <d-form class="main-navbar__search w-100 d-none d-md-flex d-lg-flex" style="margin-bottom: 0 !important">
        <d-input-group class="ml-3" seamless>
            <d-input-group-text slot="prepend">
                <i class="material-icons">search</i>
            </d-input-group-text>
            <d-input class="navbar-search" style="padding-left: 40px !important" @change="onRepo" placeholder="Repository Search Coming Soon!" />
        </d-input-group>
    </d-form>
</template>

<script lang="ts">
import { mapActions, mapGetters, mapMutations } from "vuex";
import Component from 'vue-class-component';
import Vue from 'vue';

@Component({
  methods: {
    ...mapActions('common',[
    	'retrieveRepoIds'
    ])
  },
  computed: {
    ...mapGetters('common', [
    	'AugurAPI'
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

    onRepo (e:any) {

    	let group = e.target.value.split('/').length > 1 ? e.target.value.split('/')[0] : null
    	let repo = e.target.value.split('/').length > 1 ? e.target.value.split('/')[1] : e.target.value.split('/')[0]
    	alert(group + " " + repo)
    	this.retrieveRepoIds({
			repo: repo,
			rg_name: group
        }).then((ids: any) => {
			this.$router.push({
				name: 'repo_overview',
				params: {'group': ids.rg_name, 'repo': repo, 'repo_group_id': ids.repo_group_id, 'repo_id': ids.repo_id}
			})
		})

    }
};

</script>
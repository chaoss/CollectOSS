export default {
    comparison_type: (state:any) => {
        if (state.comparedRepos.length == 0 && state.comparedRepoGroups.length == 0 ) {
            return 'Single Repo'
        }
        if (state.comparedRepos.length == 0 && state.comparedRepoGroups.length == 0) {
            return 'Single Repo Group'
        }
        else if (state.comparedRepos.length == 1 && state.comparedRepoGroups.length == 0) {
            return '1-on-1 repo comparison'
        }
        else if (state.comparedRepoGroups.length == 1 && state.comparedRepos.length == 0) {
            return '1-on-1 group comparison'
        }
        else if (state.comparedRepos.length == 0 && state.comparedRepoGroups.length > 1) {
            return "Multiple Groups"
        }
        else if (state.comparedRepos.length > 1 && state.comparedRepoGroups.length == 0) {
            return "Custom Group"
        }
        else if (state.comparedRepos.length == 0 && state.comparedRepoGroups.length == 0) {
            return "Comparison Type N/A"
        }
        else {
            return "Invalid comparison type"
        }
    },
    repo: (state:any, getters:any, rootState:any, rootGetters:any) => {
        console.log("####", rootGetters['common/getRepoByURL'](state.baseRepo) || {'url': 'No base repo selected'})
        return  rootGetters['common/getRepoByURL'](state.baseRepo) || {'url': 'No base repo selected'}
    }
};

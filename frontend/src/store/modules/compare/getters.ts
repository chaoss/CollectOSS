import construct = Reflect.construct;

export default {
    comparisonType: (state:any) => {
        if (state.baseRepo == '' && state.baseGroup == '') {
            return 'Comparison Type N/A'
        }

        if (state.comparedRepos.length == 0 && state.comparedRepoGroups.length == 0 && state.baseRepo != '') {
            return 'Single Repo'
        }

        if (state.comparedRepos.length == 0 && state.comparedRepoGroups.length == 0 && state.baseGroup != '') {
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
    // return the base
    base: (state:any, getters:any, rootState:any, rootGetters:any) => {
        if(state.baseRepo) {
            return rootGetters['common/getRepoByURL'](state.baseRepo) || {'url': 'No base repo/group selected'}
        } else if (state.baseGroup) {
            return rootGetters['common/repoGroups'][state.baseGroup] || {'url': 'No base repo/group selected'}
        }

        return {'url': 'No base repo/group selected'}
    },

    isDefinedType: (state:any, getters:any, rootState:any, rootGetters:any) => {
        if(state.baseRepo == '' || state.baseGroup == '') {
            return false
        } else {
            return true
        }
    },

    comparisionSize: (state:any) => {
        if(state.comparedRepos.length != 0) {
            return state.comparedRepos.length
        } else if (state.comparedRepoGroups.length) {
            return state.comparedRepoGroups.length
        }
        return  'No'
    }

};

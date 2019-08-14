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
            return rootGetters['common/apiRepos'][state.baseRepo] || {'url': 'No base repo/group selected'}
        } else if (state.baseGroup) {
            return rootGetters['common/apiGroups'][state.baseGroup] || {'url': 'No base repo/group selected'}
        }

        return {}
    },

    isGroup: (state:any, getters:any, rootState:any, rootGetters:any) => {
        if(state.baseGroup != ''){
            return true
        } else {
            return false
        }
    },

    comparisionSize: (state:any) => {
        if(state.comparedRepos.length != 0) {
            return state.comparedRepos.length
        } else if (state.comparedRepoGroups.length) {
            return state.comparedRepoGroups.length
        }
        return  'No'
    },
    compare: (state:any) => {
        return state.compare
    },
    trailingAverage: (state:any) => {
        return state.trailingAverage
    },
    showArea: (state:any) => {
        return state.showArea
    },
    startDate: (state:any) => {
        return state.startDate
    },
    endDate: (state:any) => {
        return state.endDate
    },
    showDetail: (state:any) => {
        return state.showDetail
    },
    showTooltip: (state:any) => {
        return state.showTooltip
    },
    byDate: (state:any) => {
        return state.byDate
    },
    rawWeekly: (state:any) => {
        return state.byDate
    },
    showBelowAverage: (state:any) => {
        return state.showBelowAverage
    },
    comparedRepoGroups: (state:any) => {
        return  state.comparedRepoGroups
    },
    comparedRepos: (state:any) => {
        return state.comparedRepos
    },
};

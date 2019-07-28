export default {
    async addComparedRepo(context:any, payload:any) {
        context.state.compare = 'zcore';
        if (context.state.baseRepo == ''){
            context.commit('setBaseRepo', payload)
        }
        if(!context.state.comparedRepos.include(payload.url) && context.state.baseRepo == payload.url) {
            context.commit('addComparedRepo', payload.url)
        }
        if (payload.rg_name in context.rootState.common.getters.repoRelationsInfo
            || payload.url in context.rootState.common.getters.repoRelationsInfo[payload.rg_name]) {
            context.dispatch('common/addRepo',payload)
        }
    },

    async addComparedGroup(context:any, payload:any) {
        context.state.compare = 'zcore';
        if (context.state.baseGroup == ''){
            context.commit('setBaseGroup', payload)
        }
        if(!context.state.comparedRepoGroups.include(payload.url) && context.state.baseRepo == payload.rg_name) {
            context.commit('addComparedRepoGroups', payload.url)
        }
        if (payload.rg_name in context.rootState.common.getters.repoGroups ) {
            context.dispatch('common/addRepoGroup',payload)
        }
    },
}
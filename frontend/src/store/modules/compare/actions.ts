export default {
    async addComparedRepo(context:any, payload:any) {

        // type is not valid
        if (context.state.baseGroup != '') {
            return
        }

        context.state.compare = 'zcore';

        if (context.state.baseRepo == ''){
            context.commit('setBaseRepo', payload)
        }
        if(!(context.state.comparedRepos.includes(payload.url) && context.state.baseRepo == payload.url)) {
            context.commit('addComparedRepo', payload.url)
        }
        if (!(payload.rg_name in context.rootGetters['common/apiRepos'])) {
            context.dispatch('common/addRepo',payload,{root:true})
        }
    },

    async addComparedGroup(context:any, payload:any) {
        // type is not valid
        if (context.state.baseRepo != '') {
            return
        }
        context.state.compare = 'zcore';
        if (context.state.baseGroup == ''){
            context.commit('setBaseGroup', payload)
        }
        if(!context.state.comparedRepoGroups.includes(payload.rg_name) && context.state.baseGroup != payload.rg_name) {
            context.commit('addComparedRepoGroups', payload.rg_name)
        }
        console.log('#####', context.rootGetters['common/apiGroups'])
        if (!(payload.rg_name in context.rootGetters['common/apiGroups'])) {
            context.dispatch('common/addRepoGroup',payload,{root:true})
        }
    },

}



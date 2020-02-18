// module for utility global state
export default {
    namespaced: true, 
    state: {
      baseEndpointUrl: 'api/unstable', 
    },
    mutation: {
      setBaseEndpointUrl(state, newValue) {
        state.baseEndpointUrl = newValue;
      }
    },
    actions: {
  
    },
    getters: {
  
    }
  }
// module for utility global state
export default {
    namespaced: true, 
    state: {
      baseEndpointUrl: 'http://localhost:5000/api/unstable', 
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
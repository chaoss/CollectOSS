const configObject = require("../../../augur.config.json");

// module for utility global state
export default {
    namespaced: true, 
    state: {
      host: configObject["Frontend"].host,
      port: configObject["Frontend"].port,
      baseEndpointUrl: `http://${configObject["Frontend"].host}:${configObject["Frontend"].port}/api/unstable`, 
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
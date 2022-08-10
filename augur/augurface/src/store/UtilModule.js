// #SPDX-License-Identifier: MIT
var configObject = require('../../../frontend/frontend.config.json')
import Vue from 'vue';

// module for utility global state
export default {
  namespaced: true,
  state: {
    host: configObject["Frontend"].host,
    port: configObject["Frontend"].port,
    baseEndpointUrl: `http${configObject["Frontend"].ssl ? "s" : ""}://${configObject["Frontend"].host}:${configObject["Frontend"].port}/api/unstable`,
    // baseEndpointUrl: 'http://localhost:5000/api/unstable',
    crudKey: sessionStorage.getItem("__augursessionstorage__crudkey") !== null ? sessionStorage.getItem("__augursessionstorage__crudkey") : '',
    availableEndpoints: [
      'http://localhost:5000/api/unstable',
      'http://augur.osshealth.io/api/unstable'
    ]
  },
  mutations: {
    setBaseEndpointUrl(state, newValue) {
      Vue.set(state, "baseEndpointUrl", newValue);
    },
    addAvailableEndpoint(state, newEndpoint) {
      Vue.set(state, "availableEndpoints", [...state.availableEndpoints, newEndpoint]);
    },
    setCrudKey(state, newKey) {
      Vue.set(state, "crudKey", newKey);
      sessionStorage.setItem("__augursessionstorage__crudkey", newKey);
    }
  },
  actions: {

  },
  getters: {
    getAvailableEndpoints(state) {
      return state.availableEndpoints;
    },
    getAvailableEndpointsForDropdown(state) {
      // maps available endpoints into array compatible with prop for AugDropdown.vue
      return state.availableEndpoints.map(endpoint => { return { text: endpoint, value: endpoint } });
    },
    getCurrentEndpointUrlForDropdown(state) {
      // maps current endpoint into object compatible with prop for AugDropDown.vue
      return { text: state.baseEndpointUrl, value: state.baseEndpointUrl };
    },
    getBaseEndpointUrl(state) {
      return state.baseEndpointUrl;
    },
    getCrudKey(state) {
      return state.crudKey;
    }
  }
}

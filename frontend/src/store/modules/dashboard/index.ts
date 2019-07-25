import axios from 'axios';
import actions from './actions';
import mutations from './mutations';
import getters from './getters';
const AugurAPIModule = require('@/AugurAPI').default;
const AugurAPI = new AugurAPIModule();

const state = {
  cache: {},
};

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations,
};

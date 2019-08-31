import axios from 'axios';
import actions from './actions';
import mutations from './mutations';
import getters from './getters';
var config = require('../../../../../augur.config.json')
const AugurAPIModule = require('@/AugurAPI').default;
var port = config['Server']['port'] ? ':' + config['Server']['port'] : ''
const AugurAPI = new AugurAPIModule('http://' + config['Server']['host'] + port);

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

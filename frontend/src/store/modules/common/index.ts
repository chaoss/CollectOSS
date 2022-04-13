// #SPDX-License-Identifier: MIT
import axios from 'axios';
import actions from './actions';
import mutations from './mutations';
import getters from './getters';

var config = require('../../../../frontend.config.json')
const AugurAPIModule = require('@/AugurAPI').default;
var port = config['Frontend'] ? (config['Frontend']['port'] ? ':' + config['Frontend']['port'] : '') : (config['Server']['port'] ? ':' + config['Server']['port'] : '')
var host = config['Frontend'] ? (config['Frontend']['host']) : (config['Server']['host'])
const AugurAPI = new AugurAPIModule('http://' + host + port);

const state = {
  // hasState: false,
  // tab: 'gmd',
  // page: 'dashboard',
  apiGroups: {},
  apiRepos: {},
  AugurAPI,
  cache: {},
  baseRepo: '',
  gitRepo: '',
  baseGroup: '',
  comparedRepoGroups: new Array(),
  comparedRepos: new Array(),
  trailingAverage: 30,
  startDate: new Date('1 February 2011'),
  endDate: new Date(),
  compare: 'rolling',
  showBelowAverage: false,
  rawWeekly: false,
  showArea: true,
  showDetail: false,
  showTooltip: true,
  byDate: false,
  tab: null,
};

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations,
};

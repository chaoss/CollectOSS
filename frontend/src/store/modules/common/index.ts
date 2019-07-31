import axios from 'axios';
import actions from './actions';
import mutations from './mutations';
import getters from './getters';
const AugurAPIModule = require('@/AugurAPI').default;
const AugurAPI = new AugurAPIModule();

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
  trailingAverage: 180,
  startDate: new Date('1 February 2011'),
  endDate: new Date(),
  compare: 'rolling',
  showBelowAverage: false,
  rawWeekly: false,
  showArea: true,
  showDetail: false,
  showTooltip: true,
  byDate: false,
};

export default {
  namespaced: true,
  state,
  actions,
  getters,
  mutations,
};

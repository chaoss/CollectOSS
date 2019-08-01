import axios from 'axios';
import actions from './actions';
import mutations from './mutations';
import getters from './getters';
const AugurAPIModule = require('@/AugurAPI').default;
const AugurAPI = new AugurAPIModule();

const state = {
    baseRepo: '',
    gitRepo: '',
    baseGroup: '',
    comparedRepoGroups: new Array(),
    comparedRepos: new Array(),
    startDate: new Date('1 February 2011'),
    endDate: new Date(),
    trailingAverage: 180,
    compare: 'rolling',
    rawWeekly:false,
    showArea: true,
    showDetail: false,
    showTooltip: true,
    byDate: false,
    showBelowAverage: false,
};

export default {
    namespaced: true,
    state,
    actions,
    getters,
    mutations,
};

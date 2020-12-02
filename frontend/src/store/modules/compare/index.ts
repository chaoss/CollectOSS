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
    baseRepo: '',
    gitRepo: '',
    baseGroup: '',
    comparedRepoGroups: new Array(),
    comparedRepos: new Array(),
    startDate: new Date('1 February 2011'),
    endDate: new Date(),
    trailingAverage: 180,
    compare: 'rolling',
    rawWeekly: false,
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

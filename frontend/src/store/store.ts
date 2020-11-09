// #SPDX-License-Identifier: MIT
/* tslint:disable */
import Vue from 'vue';
import Vuex from 'vuex';
import router from '@/router'
import createPersistedState from "vuex-persistedstate"

Vue.use(Vuex);

// Modules
import common from './modules/common/index';
import compare from './modules/compare/index'

export default new Vuex.Store({
	modules: {
		common,
		compare
	},
	plugins: [createPersistedState({paths:['common.cache']})]

})

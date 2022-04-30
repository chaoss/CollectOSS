// #SPDX-License-Identifier: MIT
/* tslint:disable */
import { createStore } from 'vuex';
import createPersistedState from "vuex-persistedstate"

// Modules
import common from './modules/common/index';
import compare from './modules/compare/index'

export const store = createStore({
	modules: {
		common,
		compare
	},
	plugins: [createPersistedState({ paths: ['common.cache'] })]

})

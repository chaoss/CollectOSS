/* tslint:disable */
import Vue from 'vue';
import Vuex from 'vuex';
import router from '@/router'
import createPersistedState from "vuex-persistedstate"

Vue.use(Vuex);

// Modules
import common from './modules/common/index';

export default new Vuex.Store({
	modules: {
		common
	},
	plugins: [createPersistedState()]
})

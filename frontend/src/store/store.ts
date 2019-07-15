/* tslint:disable */
import Vue from 'vue';
import Vuex from 'vuex';
import router from '@/router'

Vue.use(Vuex);

// Modules
import common from './modules/common/index';


export default new Vuex.Store({
	modules: {
		common
	}
})

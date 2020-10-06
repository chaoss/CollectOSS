// #SPDX-License-Identifier: MIT
import Vue from 'vue';
import Vuex from 'vuex';
import utilModule from './UtilModule.js';
import userModule from './UserModule.js';
import reposModule from './ReposModule.js';

Vue.use(Vuex);

export default new Vuex.Store({
  modules: {
    utilModule,
    reposModule,
    userModule
  }
});
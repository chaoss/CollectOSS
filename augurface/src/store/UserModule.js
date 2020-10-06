// #SPDX-License-Identifier: MIT
// module for necessary user data
import Vue from "vue";

export default {
    namespaced: true, 
    state: {
        loggedIn: false
    }, 
    mutations: {
        setLoggedIn(state, newValue) {
            Vue.set(state, 'loggedIn', newValue);
        }
    }, 
    actions: {
        signInWithSlack: (context) => {
            context.commit("setLoggedIn", true);
        }
    }, 
    getters: {
        isLoggedIn(state) {
            return state.loggedIn;
        }
    }
}
const _ = require('lodash');
import Vue from 'vue';

// store for repo/repogroup metadata
export default {
  namespaced: true,
  state: {
    repoGroups: [],
    repos: [],
    reposLoaded: false,
    groupsLoaded: false
  },
  mutations: {
    setRepoGroups(state, newValue) {
      Vue.set(state, 'repoGroups', newValue);
    },
    setRepos(state, newValue) {
      Vue.set(state, 'repos', newValue);
    },
    setReposLoaded(state, newValue) {
      Vue.set(state, 'reposLoaded', newValue);
    },
    setGroupsLoaded(state, newValue) {
      Vue.set(state, 'groupsLoaded', newValue);
    },
    addRepos(state, newRepos) {
      Vue.set(state, 'repos', [...state.repos, ...newRepos]);
    },
    addGroup(state, newGroup) {
      Vue.set(state, 'repoGroups', [...state.repoGroups, newGroup]);
    }
  },
  actions: {
    retrieveRepos(context, checkCache) {
      // setup
      let { rootState, commit } = context;

      // check local storage for cached repos
      if (checkCache) {
        let reposRetrievedFromLocalStorage = localStorage.getItem('__augurlocalstorage__repos');
        if (reposRetrievedFromLocalStorage != null) {
          commit('setRepos', JSON.parse(reposRetrievedFromLocalStorage));
          commit('setReposLoaded', true);
          return;
        }
      }

      // make request (if nothing is in localstorage)
      return fetch(`${rootState.utilModule.baseEndpointUrl}/repos`)
        .then(res => {
          if (res.status !== 200) {
            console.log('request for loading repos failed...');
            console.dir(res);
            return null;
          } else {
            return res.json();
          }
        })
        .then(res => {
          if (res != null) {
            // filter response and update state
            let filteredResponse = res.map(repo => {
              let filteredRepo = _.pick(repo, [
                'repo_id',
                'repo_name',
                'description',
                'repo_group_id',
                'rg_name',
                'url'
              ]);
              filteredRepo.repo_group_id = String(filteredRepo.repo_group_id);
              filteredRepo.repo_id = String(filteredRepo.repo_id);
              return filteredRepo;
            })
            localStorage.setItem('__augurlocalstorage__repos', JSON.stringify(filteredResponse));
            commit('setRepos', filteredResponse);
            commit('setReposLoaded', true);
          }
        });
    },
    retrieveRepoGroups(context, checkCache) {
      // setup
      let { rootState, commit } = context;

      // check local storage for cached repo groups
      if (checkCache) {
        let groupsRetrievedFromLocalStorage = localStorage.getItem('__augurlocalstorage__groups');
        if (groupsRetrievedFromLocalStorage != null) {
          commit('setRepoGroups', JSON.parse(groupsRetrievedFromLocalStorage));
          commit('setGroupsLoaded', true);
          return;
        }
      }

      // make request
      return fetch(`${rootState.utilModule.baseEndpointUrl}/repo-groups`)
        .then(res => {
          if (res.status !== 200) {
            console.log('request for loading repogroups failed...');
            console.dir(res);
            return null;
          } else {
            return res.json();
          }
        })
        .then(res => {
          if (res != null) {
            // filter response and update state
            let filteredResponse = res.map(repoGroup => {
              let filteredRG = _.pick(repoGroup, [
                'rg_name',
                'repo_group_id'
              ]);
              filteredRG.repo_group_id = String(filteredRG.repo_group_id);
              return filteredRG;
            })
            localStorage.setItem('__augurlocalstorage__groups', JSON.stringify(filteredResponse));
            commit('setRepoGroups', filteredResponse);
            commit('setGroupsLoaded', true);
          }

        });
    }
  },
  getters: {
    isLoaded(state) {
      return state.reposLoaded && state.groupsLoaded;
    },
    isGroupsLoaded(state) {
      return state.groupsLoaded;
    },
    getReposInGroup: (state) => (rg_id) => {
      return state.repos.filter(repo => repo.repo_group_id === rg_id);
    },
    getRepoGroups(state) {
      return state.repoGroups;
    }
  }
}
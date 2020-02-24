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
      sessionStorage.setItem('__augursessionstorage__repos', JSON.stringify(state.repos));
    },
    addGroup(state, newGroup) {
      Vue.set(state, 'repoGroups', [...state.repoGroups, newGroup]);
      sessionStorage.setItem('__augursessionstorage__groups', JSON.stringify(state.repoGroups));
    }
  },
  actions: {
    retrieveRepos(context, checkCache) {
      // setup
      let { rootState, commit } = context;

      // check local storage for cached repos
      if (checkCache) {
        let reposRetrievedFromSessionStorage = sessionStorage.getItem('__augursessionstorage__repos');
        if (reposRetrievedFromSessionStorage != null) {
          commit('setRepos', JSON.parse(reposRetrievedFromSessionStorage));
          commit('setReposLoaded', true);
          return;
        }
      }

      // make request (if nothing is in sessionStorage)
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
            sessionStorage.setItem('__augursessionstorage__repos', JSON.stringify(filteredResponse));
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
        let groupsRetrievedFromSessionStorage = sessionStorage.getItem('__augursessionstorage__groups');
        if (groupsRetrievedFromSessionStorage != null) {
          commit('setRepoGroups', JSON.parse(groupsRetrievedFromSessionStorage));
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
            sessionStorage.setItem('__augursessionstorage__groups', JSON.stringify(filteredResponse));
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
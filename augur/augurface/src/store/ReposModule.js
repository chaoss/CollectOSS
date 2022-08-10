// #SPDX-License-Identifier: MIT
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
      let nonConflictingPreviousRepos = state.repos.filter(r => newRepos.find(re => re.repo_id === r.repo_id) == null);
      Vue.set(state, 'repos', [...nonConflictingPreviousRepos, ...newRepos]);
      sessionStorage.setItem('__augursessionstorage__repos', JSON.stringify(state.repos));
    },
    addGroup(state, newGroup) {
      if (state.repoGroups.find(rg => rg.repo_group_id === newGroup.repo_group_id) == null) {
        Vue.set(state, 'repoGroups', [...state.repoGroups, newGroup]);
        sessionStorage.setItem('__augursessionstorage__groups', JSON.stringify(state.repoGroups));
      }
    }
  },
  actions: {
    addRepos: (context, requestBody) => {
      return fetch(`${context.rootState.utilModule.baseEndpointUrl}/add-repos`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestBody)
      })
        .then(res => {
          console.log(`STATUS: ${res.status}`);
          if (res.status === 401) {
            alert("Database key is missing. Please enter the key provided at database creation in the field on top-right corner of page.");
          }
          if (res.status === 200) {
            return res.json();
          } else {
            return null;
          }
        })
        .then(res => {
          if (res) {
            // update state
            context.commit("addRepos", res.repos_inserted);

            // check for failed adds
            if (res.repos_not_inserted.invalid_inputs.length > 0) {
              window.alert(
                `${res.repos_inserted.length} repos successfully added\n${res.repos_not_inserted.invalid_inputs.length} repos failed\ncheck console for detail`
              );
              console.log("following repos failed to be inserted: ");
              console.log(res.repos_not_inserted.invalid_inputs);
            }
          }
        });
    },
    importGroup: (context, orgName) => {
      if (orgName === '') {
        window.alert("invalid org name");
        return;
      }
      let requestObject = {
        org: orgName,
        augur_api_key: context.rootState.utilModule.crudKey
      };
      return fetch(`${context.rootState.utilModule.baseEndpointUrl}/import-org`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(requestObject)
      })
        .then(res => {
          if (res.status === 500) {
            console.log("Server error (possible invalid organization name)");
            window.alert(
              "Possible invalid organization name entered. Import failed."
            );
            return null;
          } else if (res.status === 401) {
            alert("Database key is missing. Please enter the key provided at database creation in the field on top-right corner of page.");
            return null;
          } else {
            return res.json();
          }
        })
        .then(res => {
          if (res != null) {
            if (res.group_errors.length > 0) {
              window.alert(res.group_errors[0]);
              return;
            }
            window.alert("successfully imported github organization");
            context.commit(
              "addRepos",
              res.repo_records_created
            );
            context.commit("addGroup", {
              repo_group_id: res.group_id,
              rg_name: res.rg_name
            });
          }
        });
    },
    createGroup: (context, groupName) => {
      console.log(groupName);
      let requestObject = {
        group: groupName,
        augur_api_key: context.rootState.utilModule.crudKey
      };
      return fetch(
        `${context.rootState.utilModule.baseEndpointUrl}/create-repo-group`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify(requestObject)
        }
      )
        .then(res => {
          if (res.status === 200) {
            return res.json();
          } else if (res.status === 401) {
            alert("Database key is missing. Please enter the key provided at database creation in the field on top-right corner of page.");
            return null;
          } else {
            window.alert("unable to create group");
            return null;
          }
        })
        .then(res => {
          if (res != null) {
            console.log(res);
            if (res.errors == null) {
              alert("Database key is missing. Please enter the key provided at database creation in the field on top-right corner of page.");
              return null;
            }
            if (res.errors.length > 0) {
              window.alert(res.errors[0]);
              return;
            }
            window.alert("successfully created group");
            let groupCreated = res["repo_groups_created"][0];
            console.log(groupCreated);
            context.commit("addGroup", {
              repo_group_id: String(groupCreated.repo_group_id),
              rg_name: groupCreated.rg_name
            });
          }
        });
    },
    refreshRepos(context) {
      console.log(context);
      context.commit("setReposLoaded", false);
      context.commit("setGroupsLoaded", false);
      context.dispatch("retrieveRepoGroups", false);
      context.dispatch("retrieveRepos", false);
    },
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
          console.log(res.status);
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
            let filteredResponse = [];
            filteredResponse = res.map(repo => {
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
            console.log(filteredResponse);
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
    },
    repoCountInGroup: (state) => (rg_id) => {
      return state.repos.filter(repo => repo.repo_group_id === rg_id).length;
    }
  }
}
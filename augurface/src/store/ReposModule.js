const _ = require('lodash');

// store for repo/repogroup metadata
export default  {
    namespaced: true, 
    state: {
      repoGroups: [], 
      repos: [], 
      reposLoaded: false, 
      groupsLoaded: false
    },
    mutations: {
      setRepoGroups(state, newValue) {
        state.repoGroups = newValue;
      }, 
      setRepos(state, newValue) {
          state.repos = newValue;
      }, 
      setReposLoaded(state, newValue) {
        state.reposLoaded = newValue;
      }, 
      setGroupsLoaded(state, newValue) {
        state.groupsLoaded = newValue;
      }, 
    },
    actions: {
        retrieveRepos(context) {
            // setup
        let { rootState, commit } = context;

        // make request
        return fetch(`http://localhost:5000/${rootState.utilModule.baseEndpointUrl}/repos`)
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
                // update state
                let filteredResponse = res.map(repoGroup => {
                    let filteredRG = _.pick(repoGroup, [
                        'repo_id', 
                        'repo_name', 
                        'description', 
                        'repo_group_id', 
                        'rg_name', 
                        'url'
                    ]);
                    return filteredRG;
                })
                commit('setRepos', filteredResponse);
                commit('setReposLoaded', true);
            }

          });
        }, 
      retrieveRepoGroups(context) {
        // setup
        let { rootState, commit } = context;

        // make request
        return fetch(`http://localhost:5000/${rootState.utilModule.baseEndpointUrl}/repo-groups`)
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
                // update state
                let filteredResponse = res.map(repoGroup => {
                    let filteredRG = _.pick(repoGroup, [
                        'rg_name', 
                        'repo_group_id'
                    ]);
                    return filteredRG;
                })
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
      }
    }
  }
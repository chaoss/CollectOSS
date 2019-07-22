export default {
    repoRelationsInfo: (state: any) => {
      return state.repoRelationsInfo;
    },
    groupsInfo: (state: any) => {
      return state.groupsInfo;
    },
    groupsList: (state: any) => {
      return Object.keys(state.groupsInfo);
    },
    AugurAPI: (state: any) => {
      return state.AugurAPI;
    },
};

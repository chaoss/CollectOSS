# AugurFace Documentation
## Installation for development
* navigate to the augur/augurface directory
* run 'npm install' 
* run 'npm run serve' to deploy the app locally
---
## Global Data
* AugurFace is a Vue application, and uses Vuex for global data management.<br> Vuex has great documentation here: https://vuex.vuejs.org/
<br>Vue also has useful documentation here: https://vuejs.org
* You can find code related to vuex in augur/augurface/src/store.<br>Currently, the data stored in Vuex is kept minimal on purpose

```

reposModule
  --repoGroups (metadata about loaded repo groups)
  --repos (metadata about loaded repos)

utilModule
  --baseEndpointUrl (url of server to make requests to)

userModule (this module is empty for now, but will be used for SSO in the future)

```

* To access global data from a component, you can use 'this.$store.state.[module].[attribute]
<br>e.g this.$store.state.reposModule.repos can be used within a component to access an array of the currently loaded groups

* Understanding state, mutations, and actions, and getters are important before contributing to AugurFace

---

## Component Structure / Router
* AugurFace uses VueRouter to manage routes with a single page application<br>Documentation on VueRouter can be found here: router.vuejs.org <br>Code related to the router can be found in augur/augurface/src/router/
* Components that are used for page layouts (Login page, Dashboard bage, etc) can be found in augur/augurface/src/layouts/
* Other components are in augur/augurface/src/components
* Components that are very modular by nature (wrapped html elements, icon buttons, etc) are kept in the components/BaseComponents/ directory
# STYLE
* Global styles (mainly CSS variables) are within public/index.html
* Any other style should be scoped to a component or carefully managed in a parent component (for modularity)

# COMPONENT ORGANIZATION
* Components use the SFC (Single File Component) structure for readability and ease of debugging. This is a Vue 2.0 standard
* The organization of components within the directory is done in an effort to mimic the tree of Vue components when rendering.
* The main rule being that, when a component is almost guarenteed to only be nested within another component (and no other component), it should be in a directory within that components directory
* Components that are in multiple components should be at the highest level component where that component could be found (e.g if there is a component that will be in multiple components, but only components nested in Dashboard.vue, then that component should be within the Dashboard directory)

# STATE MANAGEMENT
* Vuex is used for global state data
* If you are unfamiliar with Vuex, reading the following page would be helpful https://vuex.vuejs.org/guide/
* Ideally, the global state should provide enough information to make any requests specific components will need but should leave a small footprint.
* repogroup metadata (id, name, etc), repo metadata (id, name, etc), and user metadata (token, username, etc) are good things to store within the state
* the store is split into three modules currently. reposModule, userModule and utilModule
# STYLE
* Global styles (mainly CSS variables) are within public/index.html
* Any other style should be scoped to a component or carefully managed in a parent component (for modularity)

# COMPONENT ORGANIZATION
* Components use the SFC (Single File Component) structure for readability and ease of debugging. This is a Vue 2.0 standard
* The organization of vue components is a little out of the regular. This is done in an effort to make it easy for developers to track down where a UI element they see on the webpage is located in code immediately. If these rules are followed than the components directory can be navigated through as if you were navigating through the tree of components created by Vue when served to viewer
* Rules
  * Any 'view' is in a folder in components (e.g The Login view is in /src/components/Login/Login.vue)
  * Any components specific to that view will also be in this folder (e.g LoginCard.vue is in /src/components/Login/LoginCard.vue)
  * Any general components used in multiple views are just in the components directory
  * Any folder anywhere within /src/components that doesn't begin with a capital letter represents a non-view component with one or more child components specific to it (e.g src/components/Dashboard/dashboardHeader/DashboardHeader.vue requires child components src/.../dashboardHeader/NavBar.vue and src/.../dashboardHeader/NavLink.vue)
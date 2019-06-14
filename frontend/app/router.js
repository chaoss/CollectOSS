import Vue from 'vue'
import Router from 'vue-router'
import MetricsStatusCard from './components/MetricsStatusCard.vue'
import BaseRepoActivityCard from './components/BaseRepoActivityCard.vue'
import BaseRepoEcosystemCard from './components/BaseRepoEcosystemCard.vue'
import GrowthMaturityDeclineCard from './components/GrowthMaturityDeclineCard'
import RiskCard from './components/RiskCard'
import ValueCard from './components/ValueCard'
import DiversityInclusionCard from './components/DiversityInclusionCard'
import GitCard from './components/GitCard'
import OverviewCard from './components/OverviewCard.vue'
import ExperimentalCard from './components/ExperimentalCard'
import DownloadedReposCard from './components/DownloadedReposCard.vue'
import LoginForm from './components/LoginForm'
import AugurCards from './components/AugurCards.vue'
import MainControls from './components/MainControls.vue'
import AugurHeader from './components/AugurHeader.vue'
import Tabs from './components/Tabs.vue'
import TableView from './components/TableView.vue'

import PersonalBlog from './views/PersonalBlog.vue';
import UserProfileLite from './views/UserProfileLite.vue';
import AddNewPost from './views/AddNewPost.vue';
import Errors from './views/Errors.vue';
import ComponentsOverview from './views/ComponentsOverview.vue';
import Tables from './views/Tables.vue';
import BlogPosts from './views/BlogPosts.vue';
import Default from './layouts/Default.vue';
import MainSidebar from './components/layout/MainSidebar/MainSidebar.vue';
import MainNavbar from './components/layout/MainNavbar/MainNavbar.vue';
import RepoOverview from './views/RepoOverview.vue';
import RepoGroups from './views/RepoGroups.vue';
import Repos from './views/Repos.vue';

let routes = [
      {
            path: '/',
            component: Default,
            children: [
                  {
                        path: "",
                        name: "home",
                        components: {
                              sidebar: MainSidebar,
                              navbar: MainNavbar,
                              content: BlogPosts
                        }
                  }
            ]
      },
      {
            path: '/repo_groups',
            component: Default,
            children: [
                  {
                        path: "",
                        name: "repo_groups",
                        components: {
                              sidebar: MainSidebar,
                              navbar: MainNavbar,
                              content: RepoGroups
                        }
                  }
            ]
      },
      {
            path: '/workers',
            component: Default,
            children: [
                  {
                        path: "",
                        name: "workers",
                        components: {
                              sidebar: MainSidebar,
                              navbar: MainNavbar,
                              content: Tables
                        }
                  }
            ]
      },
      {
            path: '/repos',
            component: Default,
            children: [
                  {
                        path: "",
                        name: "repos",
                        components: {
                              sidebar: MainSidebar,
                              navbar: MainNavbar,
                              content: Repos
                        }
                  }
            ]
      },
      {
            path: '/insights',
            component: Default,
            children: [
                  {
                        path: "",
                        name: "insights",
                        components: {
                              sidebar: MainSidebar,
                              navbar: MainNavbar,
                              content: Tables
                        }
                  }
            ]
      },
      {
            path: '/repo/:owner?/:repo',
            component: Default,
            children: [
                  {
                        path: "",
                        name: "repo_overview",
                        components: {
                              sidebar: MainSidebar,
                              navbar: MainNavbar,
                              content: RepoOverview
                        }
                  }
            ]
      },
    {
      path: '/blog-overview',
      name: 'blog-overview',
      component: PersonalBlog,
    },
    {
      path: '/user-profile-lite',
      name: 'user-profile-lite',
      component: UserProfileLite,
    },
    {
      path: '/add-new-post',
      name: 'add-new-post',
      component: AddNewPost,
    },
    {
      path: '/errors',
      name: 'errors',
      component: Errors,
    },
    {
      path: '/components-overview',
      name: 'components-overview',
      component: ComponentsOverview,
    },
    {
      path: '/tables',
      name: 'tables',
      component: Tables,
    },
    {
      path: '/blog-posts',
      name: 'blog-posts',
      component: BlogPosts,
    }, {
      path: '*',
      redirect: '/errors',
    },
      //   {path: '/', component: Default,
      //   // children: [
      //   //   {
      //   //     path: "",
      //   //     name: "reposcard",
      //   //     components: {
      //   //       header: AugurHeader,
      //   //       content: DownloadedReposCard
      //   //     }
      //   //   },
      //   // ]
      // },
      // {path: '/login', component: LoginForm},
      // {path: '/metrics_status', 
      //   component: MetricsStatusCard
      // }, 
      // {path: '/single/:owner?/:repo', name: 'single', props: true, canReuse: false, component: AugurCards,
      //   children: [
      //     {
      //       path: "gmd",
      //       name: "gmd",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: GrowthMaturityDeclineCard
      //       }
      //     },
      //     {
      //       path: "diversityinclusion",
      //       name: "diversityinclusion",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: DiversityInclusionCard
      //       }
      //     },
      //     {
      //       path: "risk",
      //       name: "risk",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: RiskCard
      //       }
      //     },
      //     {
      //       path: "activity",
      //       name: "activity",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: BaseRepoActivityCard
      //       }
      //     },
      //     {
      //       path: "value",
      //       name: "value",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: ValueCard
      //       }
      //     },
      //     {
      //       path: "experimental",
      //       name: "experimental",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: ExperimentalCard
      //       }
      //     },
      //     {
      //       path: "git",
      //       name: "git",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: GitCard
      //       }
      //     },
      //     {
      //       path: "overview",
      //       name: "overview",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: OverviewCard
      //       }
      //     },
      //   ]
      // },
      // // {path: '/:tab/:domain/:owner/:repo/comparedto/:comparedowner/:comparedrepo', component: AugurCards, name: 'gitsinglecompare'},
      // {path: '/compare/:owner?/:repo/comparedto/:comparedowner/:comparedrepo', component: AugurCards, name: 'singlecompare', props: true, canReuse: false,
      //   children: [
      //     {
      //       path: "gmd",
      //       name: "gmdcompare",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: GrowthMaturityDeclineCard
      //       }
      //     },
      //     {
      //       path: "diversityinclusion",
      //       name: "diversityinclusioncompare",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: DiversityInclusionCard
      //       }
      //     },
      //     {
      //       path: "risk",
      //       name: "riskcompare",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: RiskCard
      //       }
      //     },
      //     {
      //       path: "value",
      //       name: "valuecompare",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: ValueCard
      //       }
      //     },
      //     {
      //       path: "activity",
      //       name: "activitycompare",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: BaseRepoActivityCard
      //       }
      //     },
      //     {
      //       path: "experimental",
      //       name: "experimentalcompare",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: ExperimentalCard
      //       }
      //     },
      //     {
      //       path: "git",
      //       name: "gitcompare",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: GitCard
      //       }
      //     },
      //   ]
      // },
      // {path: '/groupcompare/:groupid', component: AugurCards, name: 'group', props: true, canReuse: false,
      //   children: [
      //     {
      //       path: "gmd",
      //       name: "gmdgroup",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: GrowthMaturityDeclineCard
      //       }
      //     },
      //     {
      //       path: "diversityinclusion",
      //       name: "diversityinclusiongroup",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: DiversityInclusionCard
      //       }
      //     },
      //     {
      //       path: "risk",
      //       name: "riskgroup",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: RiskCard
      //       }
      //     },
      //     {
      //       path: "value",
      //       name: "valuegroup",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: ValueCard
      //       }
      //     },
      //     {
      //       path: "activity",
      //       name: "activitygroup",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: BaseRepoActivityCard
      //       }
      //     },
      //     {
      //       path: "experimental",
      //       name: "experimentalgroup",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: ExperimentalCard
      //       }
      //     },
      //     {
      //       path: "git",
      //       name: "gitgroup",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: GitCard
      //       }
      //     },
      //     {
      //       path: "overview",
      //       name: "overviewgroup",
      //       components: {
      //         header: AugurHeader,
      //         tabs: Tabs,
      //         controls: MainControls,
      //         content: OverviewCard
      //       }
      //     },
        // ]
      // },
]
let downloadedRepos = [], repos = [], projects = []
window.AugurAPI.getDownloadedGitRepos().then((data) => {

  repos = window._.groupBy(data, 'project_name')
  projects = Object.keys(repos)

})
// const routes = routerOptions.map(route => {
//   // let route1 = Object.assign({}, route);
//   return {
//     route,
//     component: () => require(`@/components/${route.component}.vue`)
//   }
// })


export default new Router({
  // routes,
  routes,
  mode: 'history',
  hashbang: false
})
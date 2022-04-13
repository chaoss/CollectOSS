// #SPDX-License-Identifier: MIT
// import Vue from 'vue';
/* tslint:disable */
import Vue from 'vue';
import Router from 'vue-router';
import store from '@/store/store';

Vue.use(Router);
import _ from 'lodash';

var config = require('../frontend.config.json')
const AugurAPIModule = require('@/AugurAPI').default;
var port = config['Frontend'] ? (config['Frontend']['port'] ? ':' + config['Frontend']['port'] : '') : (config['Server']['port'] ? ':' + config['Server']['port'] : '')
var host = config['Frontend'] ? (config['Frontend']['host']) : (config['Server']['host'])
const AugurAPI = new AugurAPIModule('http://' + host + port);

import Errors from './views/Errors.vue';
import Tables from './views/Tables.vue';
import Dashboard from './views/Dashboard.vue';
import EditConfig from './views/EditConfig.vue';
import Default from './layouts/Default.vue';
import MainSidebar from './components/layout/MainSidebar/MainSidebar.vue';
import MainNavbar from './components/layout/MainNavbar/MainNavbar.vue';
import RepoOverview from './views/RepoOverview.vue';
import GroupOverview from './views/GroupOverview.vue';
import RepoGroups from './views/RepoGroups.vue';
import Repos from './views/Repos.vue';
import SingleComparison from './views/SingleComparison.vue';
import Workers from './views/Workers.vue';
import ExploreInsights from './views/ExploreInsights.vue';
import InspectInsight from './views/InspectInsight.vue';
import RiskMetrics from "@/views/RiskMetrics.vue";
import NProgress from "nprogress";
import SlackConfig from './views/SlackConfig.vue';

const routes = [
  {
    path: '/insights',
    component: Default,
    children: [
      {
        path: '',
        name: 'home',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: Dashboard,
        },
      },
    ],
  },
  {
    path: '/slack-config',
    component: Default,
    children: [
      {
        path: '',
        name: 'slack_config',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: SlackConfig,
        },
      },
    ],
  },
  {
    path: '/', //repo_groups
    component: Default,
    children: [
      {
        path: '',
        name: 'repo_groups',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: RepoGroups,
        },
      },
    ],
  },
  {
    path: '/workers',
    component: Default,
    children: [
      {
        path: '',
        name: 'workers',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: Workers,
        },
      },
    ],
  },
  {
    path: '/repos',
    component: Default,
    children: [
      {
        path: '',
        name: 'repos',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: Repos,
        },
      },
    ],
  },
  // {
  //   path: '/insights',
  //   component: Default,
  //   children: [
  //     {
  //       path: '',
  //       name: 'insights',
  //       components: {
  //         sidebar: MainSidebar,
  //         navbar: MainNavbar,
  //         content: ExploreInsights,
  //       },
  //     },
  //   ],
  // },
  {
    path: '/config',
    component: Default,
    children: [
      {
        path: '',
        name: 'config',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: EditConfig,
        },
      },
    ],
  },
  {
    path: '/inspect_insight/:group/:repo/:metric',
    component: Default,
    children: [
      {
        path: '',
        name: 'inspect_insight',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: InspectInsight,
        },
      }
    ],
  },
  {
    path: '/repo/:group/:repo',
    component: Default,
    children: [
      {
        path: 'overview',
        name: 'repo_overview',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: RepoOverview,
        },
      },
      {
        path: 'risk',
        name: 'repo_risk',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: RiskMetrics,
        },
      },
    ],
  },
  {
    path: '/repo/:group/:repo/comparedTo/:compares',
    component: Default,
    children: [
      {
        path: '',
        name: 'repo_overview_compare',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: SingleComparison,
        },
      },
      {
        path: 'risk',
        name: 'repo_risk_compare',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: RiskMetrics,
        }
      }
    ],
  },
  {
    path: '/group/:group',
    component: Default,
    children: [
      {
        path: 'overview',
        name: 'group_overview',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: GroupOverview,
        },
      },
    ],
  },
  {
    path: '/group/:group/comparedTo/:compares',
    component: Default,
    children: [
      {
        path: 'overview',
        name: 'group_overview_compare',
        components: {
          sidebar: MainSidebar,
          navbar: MainNavbar,
          content: SingleComparison,
        },
      },
    ],
  },
  {
    path: '/errors',
    name: 'errors',
    component: Errors,
  },
  {
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
];
// let downloadedRepos = [], repos = {}, projects = [];
// console.log(window)
// console.log(AugurAPI)
// AugurAPI.getDownloadedGitRepos().then((data: any) => {

//   repos = _.groupBy(data, 'project_name');
//   projects = Object.keys(repos);

// });
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
});

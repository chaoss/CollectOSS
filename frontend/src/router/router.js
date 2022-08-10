// #SPDX-License-Identifier: MIT
import Vue from 'vue'
import Router from 'vue-router'
import MetricsStatusCard from '../components/MetricsStatusCard'
import BaseRepoActivityCard from '../components/BaseRepoActivityCard'
import BaseRepoEcosystemCard from '../components/BaseRepoEcosystemCard.vue'
import GrowthMaturityDeclineCard from '../components/GrowthMaturityDeclineCard'
import RiskCard from '../components/RiskCard'
import ValueCard from '../components/ValueCard'
import DiversityInclusionCard from '../components/DiversityInclusionCard'
import GitCard from '../components/GitCard'
import OverviewCard from '../components/OverviewCard.vue'
import IssuesCard from '../components/IssuesCard'
import ExperimentalCard from '../components/ExperimentalCard'
import DownloadedReposCard from '../components/DownloadedReposCard.vue'
import LoginForm from '../components/LoginForm'
import AugurCards from '../components/AugurCards.vue'
import MainControls from '../components/MainControls.vue'
import AugurHeader from '../components/AugurHeader.vue'
import Tabs from '../components/Tabs.vue'
import TableView from '../components/TableView.vue'
import ProjectDropdown from '../components/ProjectDropdown.vue'

let routes = [
      {path: '/', component: AugurCards,
        children: [
          {
            path: "",
            name: "reposcard",
            components: {
              header: AugurHeader,
              // tabs: ProjectDropdown,
              content: DownloadedReposCard,
              // controls: OverviewCard
            }
          },
        ]
      },
      {path: '/login', component: LoginForm},
      {path: '/metrics_status', 
        component: MetricsStatusCard
      }, 
      {path: '/single/:owner?/:repo', name: 'single', props: true, canReuse: false, component: AugurCards,
        children: [
          {
            path: "gmd",
            name: "gmd",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: GrowthMaturityDeclineCard
            }
          },
          {
            path: "diversityinclusion",
            name: "diversityinclusion",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: DiversityInclusionCard
            }
          },
          {
            path: "risk",
            name: "risk",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: RiskCard
            }
          },
          {
            path: "activity",
            name: "activity",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: BaseRepoActivityCard
            }
          },
          {
            path: "value",
            name: "value",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: ValueCard
            }
          },
          {
            path: "experimental",
            name: "experimental",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: ExperimentalCard
            }
          },
          {
            path: "git",
            name: "git",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              content: GitCard
            }
          },
          {
            path: "overview",
            name: "overview",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              content: OverviewCard
            }
          },
          {
            path: "issues",
            name: "issues",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              content: IssuesCard
            }
          },
        ]
      },
      // {path: '/:tab/:domain/:owner/:repo/comparedto/:comparedowner/:comparedrepo', component: AugurCards, name: 'gitsinglecompare'},
      {path: '/compare/:owner?/:repo/comparedto/:comparedowner/:comparedrepo', component: AugurCards, name: 'singlecompare', props: true, canReuse: false,
        children: [
          {
            path: "gmd",
            name: "gmdcompare",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: GrowthMaturityDeclineCard
            }
          },
          {
            path: "diversityinclusion",
            name: "diversityinclusioncompare",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: DiversityInclusionCard
            }
          },
            
          {
            path: "risk",
            name: "riskcompare",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: RiskCard
            }
          },
          {
            path: "value",
            name: "valuecompare",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: ValueCard
            }
          },
          {
            path: "activity",
            name: "activitycompare",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: BaseRepoActivityCard
            }
          },
          {
            path: "experimental",
            name: "experimentalcompare",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: ExperimentalCard
            }
          },
          {
            path: "git",
            name: "gitcompare",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              content: GitCard
            }
          },
        ]
      },
      {path: '/groupcompare/:groupid', component: AugurCards, name: 'group', props: true, canReuse: false,
        children: [
          {
            path: "gmd",
            name: "gmdgroup",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: GrowthMaturityDeclineCard
            }
          },
          {
            path: "diversityinclusion",
            name: "diversityinclusiongroup",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: DiversityInclusionCard
            }
          },
          {
            path: "risk",
            name: "riskgroup",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: RiskCard
            }
          },
          {
            path: "value",
            name: "valuegroup",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: ValueCard
            }
          },
          {
            path: "activity",
            name: "activitygroup",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: BaseRepoActivityCard
            }
          },
          {
            path: "experimental",
            name: "experimentalgroup",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              controls: MainControls,
              content: ExperimentalCard
            }
          },
          {
            path: "git",
            name: "gitgroup",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              content: GitCard
            }
          },
          {
            path: "overview",
            name: "overviewgroup",
            components: {
              header: AugurHeader,
              tabs: Tabs,
              content: OverviewCard
            }
          },
        ]
      },
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
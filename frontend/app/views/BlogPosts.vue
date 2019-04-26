<template>
  <d-container fluid class="main-content-container px-4">
    <!-- Page Header -->
    <div class="page-header row no-gutters py-4">
      <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
        <!-- <span class="text-uppercase page-subtitle">Components</span> -->
        <h3 class="page-title" style="font-size: 2rem">Insights</h3>
      </div>
    </div>

    <!-- First Row of Posts -->

        <d-row>
          <d-col v-for="(project, idx) in projects.slice(0,3)" :key="idx" lg="3" md="6" sm="12" class="mb-4">
            <d-card class="card-small card-post card-post--1">
              <div class="card-post__image">
                <d-badge pill :class="['card-post__category', 'bg-' + themes[idx] ]">{{ project }}</d-badge>
                <insight-chart style="transform: translateX(-30px)" :color="colors[idx]" v-if="loaded" :source="testEndpoints[idx]" owner="twitter" repo="twemoji"></insight-chart>
                <div class="card-post__author d-flex">
                  <a href="#" :style="getColor(idx)" class="card-post__author-avatar card-post__author-avatar--small" style="text-indent: 0; text-align: center; font-size: 2rem">
                    <i class="material-icons" style="position: relative; top: 50%; transform: translateY(-60%); ">{{ getDirection(idx) }}</i>
                  </a>
                </div>
              </div>
              <d-card-body>
                <h5 class="card-title">
                  <a href="#" class="text-fiord-blue">{{ getOwner(repos[project][0].url) }}/{{ getRepo(repos[project][0].url) }}</a>
                </h5>
                <p class="card-text d-inline-block mb-3">This repository {{ getPhrase(idx) }} in {{ testEndpoints[idx] }} in the past {{ testTimeframes[idx] }}</p>
                <span class="text-muted">{{ testTimeframes[idx] }}</span>
              </d-card-body>
            </d-card>
          </d-col>
          <d-col class="col-3">
            <d-card class="card-small card">
              <div class="border-bottom card-header">
                <h6 class="m-0">Worker Status</h6>
                <span class="ml-auto text-right text-semibold text-reagent-gray">Tasks Completed</span>
                <div class="block-handle"></div>
              </div>
              <div class="p-0 card-body">
                <div class="list-group-small list-group list-group-flush">
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">GitHub Shallow</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">19,291 / 21,512</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">BugZilla</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">11,201 / 14,213</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">Facade</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">9,291 / 10,634</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">Github API</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">8,281 / 15,351</span>
                  </div>
                  <div class="d-flex px-3 list-group-item">
                    <span class="text-semibold text-fiord-blue">GitHub Deep</span>
                    <span class="ml-auto text-right text-semibold text-reagent-gray">7,128 / 18,432</span>
                  </div>
                </div>
              </div>
            </d-card>
          </d-col>
        </d-row>

        <div class="page-header row no-gutters py-4" style="padding-top: 0 !important">
          <div class="col-12 col-sm-4 text-center text-sm-left mb-0">
            <!-- <span class="text-uppercase page-subtitle">Components</span> -->
            <h3 class="page-title" style="font-size: 2rem">Most Frequent Projects</h3>
          </div>
        </div>
        <!-- Second Row of Posts -->
        <d-row>
          <d-col v-for="(project, idx) in projects.slice(0,3)" :key="idx" lg="4" sm="12" class="mb-4">
            <d-card class="card-small card">
              <div class="border-bottom card-header">
                <h6 class="m-0">{{ project }}</h6>
                <div class="block-handle"></div>
              </div>
              <div class="p-0 card-body">
                <div class="list-group-small list-group list-group-flush">
                  <div v-for="(repo, i) in repos[project].slice(0,5)" class="d-flex px-3 list-group-item" style="text-align: left">
                    <span class="text-semibold text-fiord-blue">{{ repo.url }}</span>
                    <spark-chart v-if="loaded" :color="colors[idx]" style="max-height: 50px; padding-bottom: 10px; margin-left:auto; margin-right:0;" :owner="getOwner(repo.url)" :repo="getRepo(repo.url)" source="codeCommits"/>
                  </div>
                </div>
              </div>
            </d-card>
            <!-- <d-card class="card-small card-post card-post--aside card-post--1">
              <div class="card-post__image">
                <d-badge pill :class="['card-post__category', 'bg-' + post.categoryTheme ]">{{ post.category }}</d-badge>
                <div class="card-post__author d-flex">
                  <a href="#" class="card-post__author-avatar card-post__author-avatar--small">Written by Anna Ken</a>
                </div>
              </div>
              <d-card-body>
                <h5 class="card-title">
                  <a class="text-fiord-blue" href="#">{{ post.title }}</a>
                </h5>
                <p class="card-text d-inline-block mb-3">{{ post.body }}</p>
                <span class="text-muted">{{ post.date }}</span>
              </d-card-body>
            </d-card> -->
          </d-col>
        </d-row>


      
      

    

    <!-- Third Row of Posts -->
    <d-row>
      <d-col v-for="(post, idx) in PostsListThree" :key="idx" lg="4">
        <d-card class="card-small card-post mb-4">
          <d-card-body>
            <h5 class="card-title">{{ post.title }}</h5>
            <p class="card-text text-muted">{{ post.body }}</p>
          </d-card-body>
          <d-card-footer class="border-top d-flex">
            <div class="card-post__author d-flex">
              <a href="#" class="card-post__author-avatar card-post__author-avatar--small">Written by James Khan</a>
              <div class="d-flex flex-column justify-content-center ml-3">
                <span class="card-post__author-name">{{ post.author }}</span>
                <small class="text-muted">{{ post.date }}</small>
              </div>
            </div>
            <div class="my-auto ml-auto">
              <d-button size="sm" class="btn-white">
                <i class="far fa-bookmark mr-1"></i> Bookmark
              </d-button>
            </div>
          </d-card-footer>
        </d-card>
      </d-col>
    </d-row>

    <!-- Fourth Row of Posts -->
    <d-row>
      <d-col v-for="(post, idx) in PostsListFour" :key="idx" lg="3" md="6" sm="12" class="mb-4">
        <d-card class="card-small card-post h-10">
          <div class="card-post__image"></div>
          <d-card-body>
            <h5 class="card-title">
              <a class="text-fiord-blue" href="#">{{ post.title }}</a>
            </h5>
            <p class="card-text">{{ post.body }}</p>
          </d-card-body>
          <d-card-footer class="text-muted border-top py-3">
            <span class="d-inline-block">By <a class="text-fiord-blue" :href="post.authorUrl">{{ post.author }}</a> in <a class="text-fiord-blue" :href="post.categoryUrl">{{ post.category }}</a></span>
          </d-card-footer>
        </d-card>
      </d-col>
    </d-row>
  </d-container>
</template>

<script>
import SmallStats from '../components/common/SmallStats.vue';
import SparkChart from '../components/charts/SparkChart.vue';
import InsightChart from '../components/charts/InsightChart.vue';

  // Second Row of posts
const PostsListTwo = [{
  category: 'Travel',
  categoryTheme: 'info',
  author: 'Anna Ken',
  title: 'Attention he extremity unwilling on otherwise cars backwards yet',
  body: 'Conviction up partiality as delightful is discovered. Yet jennings resolved disposed exertion you off. Left did fond drew fat head poor jet pan flying over...',
  date: '29 February 2019',
}, {
  category: 'Business',
  categoryTheme: 'dark',
  author: 'John James',
  title: 'Totally words widow one downs few age every seven if miss part by fact',
  body: 'Discovered had get considered projection who favourable. Necessary up knowledge it tolerably. Unwilling departure education to admitted speaking...',
  date: '29 February 2019',
},{
  category: 'Business',
  categoryTheme: 'dark',
  author: 'John James',
  title: 'Totally words widow one downs few age every seven if miss part by fact',
  body: 'Discovered had get considered projection who favourable. Necessary up knowledge it tolerably. Unwilling departure education to admitted speaking...',
  date: '29 February 2019',
}];

  // Third Row of Posts
const PostsListThree = [{
  author: 'John James',
  title: 'Had denoting properly jointure which well books beyond',
  body: 'In said to of poor full be post face snug. Introduced imprudence see say unpleasing devonshire acceptance son. Exeter longer wisdom work...',
  date: '29 February 2019',
}, {
  author: 'John James',
  title: 'Husbands ask repeated resolved but laughter debating',
  body: 'It abode words began enjoy years no do ﻿no. Tried spoil as heart visit blush or. Boy possible blessing sensible set but margaret interest. Off tears...',
  date: '29 February 2019',
}, {
  author: 'John James',
  title: 'Instantly gentleman contained belonging exquisite now direction',
  body: 'West room at sent if year. Numerous indulged distance old law you. Total state as merit court green decay he. Steepest merit checking railway...',
  date: '29 February 2019',
}];

const PostsListFour = [{
  author: 'Alene Trenton',
  authorUrl: '#',
  category: 'News',
  categoryUrl: '#',
  title: 'Extremity so attending objection as engrossed',
  body: 'Pursuit chamber as elderly amongst on. Distant however warrant farther to of. My justice wishing prudent waiting in be...',
  date: '29 February 2019',
}, {
  author: 'Chris Jamie',
  authorUrl: '#',
  category: 'News',
  categoryUrl: '#',
  title: 'Bed sincerity yet therefore forfeited his',
  body: 'Speaking throwing breeding betrayed children my to. Me marianne no he horrible produced ye. Sufficient unpleasing and...',
  date: '29 February 2019',
}, {
  author: 'Monica Jordan',
  authorUrl: '#',
  category: 'News',
  categoryUrl: '#',
  title: 'Object remark lively all did feebly excuse our',
  body: 'Morning prudent removal an letters by. On could my in order never it. Or excited certain sixteen it to parties colonel not seeing...',
  date: '29 February 2019',
}, {
  author: 'Monica Jordan',
  authorUrl: '#',
  category: 'News',
  categoryUrl: '#',
  title: 'His followed carriage proposal entrance',
  body: 'For county now sister engage had season better had waited. Occasional mrs interested far expression directly as regard...',
  date: '29 February 2019',
}];

export default {
  components: {
    SmallStats,
    SparkChart,
    InsightChart,
  },
  computed: {
  },
  data() {
    return {
      colors: ["#343A40", "#24a2b7", "#159dfb", "#FF3647", "#4736FF","#3cb44b","#ffe119","#f58231","#911eb4","#42d4f4","#f032e6"],
      testEndpoints: ['codeCommits', 'closedIssues', 'openIssues'],
      testTimeframes: ['past 1 month', 'past 3 months', 'past 2 weeks'],
      PostsListTwo,
      PostsListThree,
      PostsListFour,
      repos: {},
      projects: [],
      themes: ['dark', 'info', 'royal-blue', 'warning'],

      smallStats: [{
        label: 'Posts',
        value: '2,390',
        percentage: '4.7%',
        increase: true,
        labels: ['Label', 'Label', 'Label', 'Label', 'Label', 'Label'],
        datasets: [{
          label: 'Today',
          fill: 'start',
          borderWidth: 1.5,
          backgroundColor: 'rgba(0, 184, 216, 0.1)',
          borderColor: 'rgb(0, 184, 216)',
          data: [1, 2, 1, 3, 5, 4, 7],
        }],
      }, {
        label: 'Pages',
        value: '182',
        percentage: '12.4',
        increase: true,
        labels: ['Label', 'Label', 'Label', 'Label', 'Label', 'Label'],
        datasets: [{
          label: 'Today',
          fill: 'start',
          borderWidth: 1.5,
          backgroundColor: 'rgba(23,198,113,0.1)',
          borderColor: 'rgb(23,198,113)',
          data: [1, 2, 3, 3, 3, 4, 4],
        }],
      }, {
        label: 'Comments',
        value: '8,147',
        percentage: '3.8%',
        increase: false,
        decrease: true,
        labels: ['Label', 'Label', 'Label', 'Label', 'Label', 'Label'],
        datasets: [{
          label: 'Today',
          fill: 'start',
          borderWidth: 1.5,
          backgroundColor: 'rgba(255,180,0,0.1)',
          borderColor: 'rgb(255,180,0)',
          data: [2, 3, 3, 3, 4, 3, 3],
        }],
      }, {
        label: 'New Customers',
        value: '29',
        percentage: '2.71%',
        increase: false,
        decrease: true,
        labels: ['Label', 'Label', 'Label', 'Label', 'Label', 'Label'],
        datasets: [{
          label: 'Today',
          fill: 'start',
          borderWidth: 1.5,
          backgroundColor: 'rgba(255,65,105,0.1)',
          borderColor: 'rgb(255,65,105)',
          data: [1, 7, 1, 3, 1, 4, 8],
        }],
      }, {
        label: 'Subscribers',
        value: '17,281',
        percentage: '2.4%',
        increase: false,
        decrease: true,
        labels: ['Label', 'Label', 'Label', 'Label', 'Label', 'Label'],
        datasets: [{
          label: 'Today',
          fill: 'start',
          borderWidth: 1.5,
          backgroundColor: 'rgb(0,123,255,0.1)',
          borderColor: 'rgb(0,123,255)',
          data: [3, 2, 3, 2, 4, 5, 4],
        }],
      }]
    };
  },
  methods: {
    getOwner(url) {
      let first = url.indexOf(".")
      let last = url.lastIndexOf(".")
      let domain = null
      let owner = null
      let repo = null
      let extension = false

      if (first == last){ //normal github
        domain = url.substring(0, first)
        owner = url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.slice(url.lastIndexOf('/') + 1)
        console.log(owner+ "/" + repo)
        return owner
      } else if (url.slice(last) == '.git'){ //github with extension
        domain = url.substring(0, first)
        extension = true
        owner = url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.substring(url.lastIndexOf('/') + 1, url.length - 4)
        return owner
      } else { //gluster
        domain = url.substring(first + 1, last)
        owner = null //url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.slice(url.lastIndexOf('/') + 1)
        return domain
      }
    },
    getRepo(url){
      let first = url.indexOf(".")
      let last = url.lastIndexOf(".")
      let domain = null
      let owner = null
      let repo = null
      let extension = false

      if (first == last){ //normal github
        domain = url.substring(0, first)
        owner = url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.slice(url.lastIndexOf('/') + 1)
        return repo
      } else if (url.slice(last) == '.git'){ //github with extension
        domain = url.substring(0, first)
        extension = true
        owner = url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.substring(url.lastIndexOf('/') + 1, url.length - 4)
        return repo
      } else { //gluster
        domain = url.substring(first + 1, last)
        owner = null //url.substring(url.indexOf('/') + 1, url.lastIndexOf('/'))
        repo = url.slice(url.lastIndexOf('/') + 1)
        return repo
      }
    },
    getColor (idx) {
      if (idx % 2 == 0)
        return 'color: green'
      else
        return 'color: red'
    },
    getDirection (idx) {
      if (idx % 2 == 0)
        return 'arrow_upward'
      else
        return 'arrow_downward'
    },
    getPhrase (idx) {
      if (idx % 2 == 0)
        return 'increased'
      else
        return 'declined'
    },
    onRepo (e) {
      this.$store.commit('setRepo', {
        githubURL: e.target.value
      })
    },
    onGitRepo (e) {
      let first = e.url.indexOf(".")
      let last = e.url.lastIndexOf(".")
      let domain = null
      let owner = null
      let repo = null
      let extension = false

      if (first == last){ //normal github
        domain = e.url.substring(0, first)
        owner = e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'))
        repo = e.url.slice(e.url.lastIndexOf('/') + 1)
      } else if (e.url.slice(last) == '.git'){ //github with extension
        domain = e.url.substring(0, first)
        extension = true
        owner = e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'))
        repo = e.url.substring(e.url.lastIndexOf('/') + 1, e.url.length - 4)
      } else { //gluster
        domain = e.url.substring(first + 1, last)
        owner = null //e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'))
        repo = e.url.slice(e.url.lastIndexOf('/') + 1)
      }
      this.$store.commit('setRepo', {
        gitURL: e.url
      })

      this.$store.commit('setTab', {
        tab: 'git'
      })

      this.$router.push({
        name: 'git',
        params: {repo: e.url}
      })
    },
    getDownloadedRepos() {
      this.downloadedRepos = []
      window.AugurAPI.getDownloadedGitRepos().then((data) => {
        $(this.$el).find('.spinner').removeClass('loader')
        $(this.$el).find('.spinner').removeClass('relative')
        this.repos = window._.groupBy(data, 'project_name')
        this.projects = Object.keys(this.repos)
        let impRepos = []
        for (let i = 0; i < this.projects.length; i++) {
          impRepos.push(this.repos[this.projects[i]][0])
        }
        console.log("LOADED")
        this.loaded = true
        // window.AugurAPI.batchMapped(impRepos, ['codeCommits']).then((data) => {
        //   console.log("DATA", data)
        // }, () => {
        //   //this.renderError()
        // }) // end batch request
      })
    },
    btoa(s) {
      return window.btoa(s)
    }
  },
  created() {
    this.getDownloadedRepos()
  },
}
</script>


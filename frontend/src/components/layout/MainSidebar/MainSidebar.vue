<!-- #SPDX-License-Identifier: MIT -->
<template>
  <aside class="main-sidebar col-1 px-0 mainSideBaraside"><!--:class="['main-sidebar', 'col-12', 'col-md-3', 'col-lg-2', 'px-0', sidebarVisible ? 'open' : '']">-->
      <div class="main-navbar">
        <nav class="navbar align-items-stretch navbar-light bg-white flex-md-nowrap border-bottom p-0">
          <a class="navbar-brand w-100 mr-0 mainSideBara" href="#">
            <div class="d-table m-auto">
              <a href="/">
                <img src="@/assets/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/>
              </a>
              <!-- <span v-if="!hideLogoText" class="d-none d-md-inline ml-1">Augur Dashboard</span> -->
            </div>
          </a>
          <a class="toggle-sidebar d-lg-none" @click="handleToggleSidebar()"> <!--d-sm-inline d-md-none d-lg-none-->
            <i class="material-icons">&#xE5C4;sfdaf</i>
          </a>
        </nav>
      </div>

      <form action="#" class="main-sidebar__search w-100 border-right d-sm-flex d-md-none d-lg-none">
        <div class="input-group input-group-seamless ml-3">
          <div class="input-group-prepend">
            <div class="input-group-text">
              <i class="fas fa-search"></i>
            </div>
          </div>
          <input class="navbar-search form-control" type="text" placeholder="Search for something..." aria-label="Search">
        </div>
      </form>

      <div class="nav-wrapper">
          <d-nav class="flex-column mainSideBarNav">
            <li v-for="(item, navItemIdx) in items" :key="navItemIdx" class="nav-item dropdown" @click="checkForRepoRouteChange($event)">
              <d-link class="mainSideBarLink" :class="['nav-link', item.items && item.items.length ? 'dropdown-toggle' : '']" :to="item.to" v-d-toggle="`snc-${navItemIdx}`">
                <div class="item-icon-wrapper" v-if="item.htmlBefore" v-html="item.htmlBefore" />
                <span v-if="item.title" class="mainSideBarV">{{ item.title }}</span>
                <div class="item-icon-wrapper" v-if="item.htmlAfter" v-html="item.htmlAfter" />
              </d-link>
              <d-collapse v-if="item.items && item.items.length" :id="`snc-${navItemIdx}`" class="dropdown-menu dropdown-menu-small" accordion="sidebar-items-accordion">
                <d-dropdown-item v-for="(subItem, subItemIdx) in item.items" :key="subItemIdx" :href="subItem.href" :to="subItem.to">
                  {{ subItem.title }}
                </d-dropdown-item>
              </d-collapse>
            </li>
            <!-- <li class="nav-item dropdown comp_manager" >
              <d-link style="font-size: 0.85rem" class="nav-link">
                <i class="material-icons">vertical_split</i>
                <span>Comparison Manager</span>
                <div class="item-icon-wrapper" />
              </d-link>
              <div style="text-align: center; border-bottom: 1px solid #e1e5eb;">
                <div class="comp_info">
                  {{comparisonType}}
                </div>
                <div class="comp_info">
                  {{  base.repo_name ? base.rg_name+'/'+base.repo_name : base.rg_name || 'No base repo/group selected'}}
                </div>
                <div class="comp_info">
                  {{comparisionSize == 0? 'No': comparisionSize}} comparison(s) selected
                </div>
              </div>
              
              <div class="row" style="position: absolute; bottom: 0; padding-left: 0px; width: 240px !important">
                <div class="col col-6" style="padding: 0px">
                  <a href="" v-on:click="onReset()">
                  <d-link class="nav-link" style="padding: 0.7rem 0.7rem 0.7rem 1.5rem; margin-left: 1rem">
                    <i class="material-icons">autorenew</i>
                    <span>Reset</span>
                    <div class="item-icon-wrapper" />
                  </d-link>
                  </a>
                </div>
                
                <div class="col col-6" style="padding: 0px">
                  <d-link class="nav-link" style="padding: 0.7rem .7rem 0.7rem 1.5rem; margin-left: 0rem">
                    <i class="material-icons">library_add</i>
                    <span>Add</span>
                    <div class="item-icon-wrapper" />
                  </d-link>
                </div>
              </div>
            </li> -->
            <li v-if="'repo_id' in base" class="mainSideBarViF"><span>Different views <p class="mainSideBarSpan">for this repo:</p></span></li>
            <li v-if="'repo_id' in base" class="mainSideBarVIF"><tab-selector></tab-selector></li>

          </d-nav>

      </div>
  </aside>
</template>

<script lang="ts">
  import Component from 'vue-class-component';
  import Vue from 'vue';
  import {mapActions, mapGetters, mapMutations} from "vuex";
  import TabSelector from "../../TabSelector.vue";
  @Component({
    props: {
      hideLogoText: {
        type: Boolean,
        default: false,
      },
    },
    components: {
      TabSelector
    },
    computed: {
      ...mapGetters('compare',[
        'base',
        'comparisonType',
        'comparisionSize',
      ])
    },
    methods: {
      ...mapMutations('compare',[
        'resetCompared',
      ])
    },
  })
  export default class MainSidebar extends Vue {
    sidebarVisible:boolean = false;
    items =  [
      {
        title: 'Insights',
        to: {
          name: 'home',
        },
        htmlBefore: '<i class="material-icons">trending_up</i>', //vertical_split
        htmlAfter: '',
      }, {
        title: 'Repos',
        to: {
          name: 'group_overview',
          params: { }
        },
        htmlBefore: '<i class="material-icons">table_chart</i>',
        htmlAfter: '',
      },
      // {
      //   title: 'Workers',
      //   to: {
      //     name: 'workers',
      //   },
      //   htmlBefore: '<i class="material-icons">assignment</i>',
      //   htmlAfter: '',
      // },
      {
        title: 'Groups',
        to: {
          name: 'repo_groups',
        },
        htmlBefore: '<i class="material-icons">group_work</i>',
        htmlAfter: '',
      },
      // {
      //   title: 'Explore Insights',
      //   to: {
      //     name: 'insights',
      //   },
      //   htmlBefore: '<i class="material-icons">trending_up</i>',
      //   htmlAfter: '',
      // },
      // {
      //   title: 'Edit Configuration',
      //   to: {
      //     name: 'config',
      //   },
      //   htmlBefore: '<i class="material-icons">assignment</i>',
      //   htmlAfter: '',
      // },
    ];
    // state declared computed
    comparisonType!: string;
    base!:string;
    resetCompared!:any;
    comparisionSize!:any;
    // method
    handleToggleSidebar() {
      this.sidebarVisible = !this.sidebarVisible;
    }
    onReset() {
      this.resetCompared()
      if (!this.$route.params.repo && this.$route.params.group) {
        this.$router.push({
          name: 'repo_groups'
        })
      }else if (this.$route.params.repo && this.$route.params.group) {
        this.$router.push({
          name: 'repos'
        })
      }
    }
    findRepoGroup() {
      console.log(Object.keys(this.$store.state.common.apiGroups));
    }
    checkForRepoRouteChange(e: any) {
      console.log(e);
      if (e.target.innerHTML !== 'Repos') {
        return;
      }
      let currentlySelectedRepoGroup = Object.keys(this.$store.state.common.apiGroups)[Object.keys(this.$store.state.common.apiGroups).length - 1].split('/')[0];
      console.log('HERE: ' + currentlySelectedRepoGroup);
      if (currentlySelectedRepoGroup === 'undefined') {
        this.$router.push({ name: 'repo_groups' });
      } else {
        this.$router.push(`group/${currentlySelectedRepoGroup}/overview`);
      }
    }
  }
</script>

<style lang="scss">
  .main-sidebar {
    .item-icon-wrapper {
      display: inline-block;
    }
    .dropdown-menu {
      display: block;
    }
  }
</style>

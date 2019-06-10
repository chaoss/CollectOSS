<template>
  <aside class="main-sidebar col-2 px-0" style="position: fixed !important"><!--:class="['main-sidebar', 'col-12', 'col-md-3', 'col-lg-2', 'px-0', sidebarVisible ? 'open' : '']">-->
      <div class="main-navbar">
        <nav class="navbar align-items-stretch navbar-light bg-white flex-md-nowrap border-bottom p-0">
          <a class="navbar-brand w-100 mr-0" href="#" style="line-height: 25px;">
            <div class="d-table m-auto">
              <a href="/">
                <img src="/static/logo.png" id="logo" alt="CHAOSS: Community Health Analytics for Open Source Software"/>
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
          <d-nav class="flex-column"> <!--style="margin: 0 !important"-->
            <li v-for="(item, navItemIdx) in items" :key="navItemIdx" class="nav-item dropdown">
              <d-link :class="['nav-link', item.items && item.items.length ? 'dropdown-toggle' : '']" :to="item.to" v-d-toggle="`snc-${navItemIdx}`">
                <div class="item-icon-wrapper" v-if="item.htmlBefore" v-html="item.htmlBefore" />
                <span v-if="item.title" style="width: 240">{{ item.title }}</span>
                <div class="item-icon-wrapper" v-if="item.htmlAfter" v-html="item.htmlAfter" />
              </d-link>
              <d-collapse v-if="item.items && item.items.length" :id="`snc-${navItemIdx}`" class="dropdown-menu dropdown-menu-small" accordion="sidebar-items-accordion">
                <d-dropdown-item v-for="(subItem, subItemIdx) in item.items" :key="subItemIdx" :href="subItem.href" :to="subItem.to">
                  {{ subItem.title }}
                </d-dropdown-item>
              </d-collapse>
            </li>
            <li class="nav-item dropdown" style="height: 240px !important; position: absolute; bottom: 0; margin-top: auto">
              <d-link style="font-size: 0.85rem" class="nav-link">
              <!-- <d-link style="font-size: 1.4rem" :class="['nav-link', item.items && item.items.length ? 'dropdown-toggle' : '']" :to="item.to" v-d-toggle="`snc-${navItemIdx}`"> -->
                <i class="material-icons">vertical_split</i>
                <span>Comparison Manager</span>
                <div class="item-icon-wrapper" />
              </d-link>
              <div class="row" style="position: absolute; bottom: 0; padding-left: 0px; width: 240px !important">
                <div class="col col-6" style="padding: 0px">
                  <d-link class="nav-link" style="padding: 0.7rem 0.7rem 0.7rem 1.5rem; margin-left: 1rem">
                    <i class="material-icons">autorenew</i>
                    <span>Reset</span>
                    <div class="item-icon-wrapper" />
                  </d-link>
                </div>
                
                <div class="col col-6" style="padding: 0px">
<!-- <<<<<<< Updated upstream -->
                  <d-link class="nav-link" style="padding: 0.7rem .7rem 0.7rem 1.5rem; margin-left: 1rem">
<!-- ======= -->
<!-- >>>>>>> Stashed changes -->
                    <i class="material-icons">library_add</i>
                    <span>Add</span>
                    <div class="item-icon-wrapper" />
                  </d-link>
                  </d-link>
                </div>
              </div>
              
              <!-- <d-collapse v-if="item.items && item.items.length" :id="`snc-${navItemIdx}`" class="dropdown-menu dropdown-menu-small" accordion="sidebar-items-accordion">
                <d-dropdown-item v-for="(subItem, subItemIdx) in item.items" :key="subItemIdx" :href="subItem.href" :to="subItem.to">
                  {{ subItem.title }}
                </d-dropdown-item>
              </d-collapse> -->
            </li>
          </d-nav>
      </div>
  </aside>
</template>

<script>
export default {
  name: 'main-sidebar',
  props: {
    hideLogoText: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      sidebarVisible: false,
      items: [
        {
          title: 'Augur Dashboard',
          to: {
            name: 'home',
          },
          htmlBefore: '<i class="material-icons">vertical_split</i>',
          htmlAfter: '',
        }, {
          title: 'Projects',
          to: {
            name: 'projects',
          },
          htmlBefore: '<i class="material-icons">table_chart</i>',
          htmlAfter: '',
        },
        {
          title: 'Workers',
          to: {
            name: 'workers',
          },
          htmlBefore: '<i class="material-icons">assignment</i>',
          htmlAfter: '',
        },
        {
          title: 'Groups',
          to: {
            name: 'groups',
          },
          htmlBefore: '<i class="material-icons">group_work</i>',
          htmlAfter: '',
        },
        {
          title: 'Explore Insights',
          to: {
            name: 'insights',
          },
          htmlBefore: '<i class="material-icons">trending_up</i>',
          htmlAfter: '',
        },

      ]
    };
  },
  methods: {
    handleToggleSidebar() {
      this.sidebarVisible = !this.sidebarVisible;
    },
  },
};
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

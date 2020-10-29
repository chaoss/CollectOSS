<!-- #SPDX-License-Identifier: MIT -->
<template>
  <d-container fluid>
    <d-row>
      <!-- Main Sidebar -->
      <!-- <d-col :class="['main-sidebar', 'col-12', 'col-md-3', 'col-lg-2', 'px-0', sidebarVisible ? 'open' : '']"> -->
      <router-view name="sidebar"></router-view>
      <!-- </d-col>   -->
       <!--<main-sidebar :items="sidebarItems" />-->

      <d-col class="main-content col-11 offset-lg-1 p-0" ><!-- offset-lg-2 offset-md-3 p-0" tag="main" lg="10" md="9" sm="12">-->

        <!-- Main Navbar -->
        <router-view name="navbar"></router-view> <!--<main-navbar />-->

        <!-- Content -->
        <router-view name="content"></router-view> <!--<slot />-->

        <main-footer></main-footer>

      </d-col>



    </d-row>
  </d-container>
</template>

<script>
// import getSidebarItems from '@/data/sidebar-nav-items';

// // Main layout components
// import MainNavbar from '@/components/layout/MainNavbar/MainNavbar.vue';
// import MainSidebar from '@/components/layout/MainSidebar/MainSidebar.vue';
import MainFooter from '@/components/layout/MainFooter/MainFooter.vue';

export default {
  name: 'analytics',
  components: {
    // MainNavbar,
    // MainSidebar,
    MainFooter,
  },
  data() {
    return {
      // sidebarItems: getSidebarItems(),
    };
  },
};
</script>


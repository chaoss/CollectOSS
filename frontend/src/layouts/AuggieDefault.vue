<template>
  <d-container fluid>
    <d-row>
      <!-- Main Sidebar -->
      <!-- <d-col :class="['main-sidebar', 'col-12', 'col-md-3', 'col-lg-2', 'px-0', sidebarVisible ? 'open' : '']"> -->
        <router-view name="sidebar"></router-view>
      <!-- </d-col>   -->
       <!--<main-sidebar :items="sidebarItems" />-->

      <d-col class="main-content col-12" ><!-- offset-lg-2 offset-md-3 p-0" tag="main" lg="10" md="9" sm="12">-->

        <!-- Main Navbar -->
        <router-view name="navbar"></router-view> <!--<main-navbar />-->

        <!-- Content -->
        <router-view name="content"></router-view> <!--<slot />-->

        <!-- Main Footer -->
        <!--<main-footer />-->
      </d-col>

    </d-row>
  </d-container>
</template>

<script>

export default {
  name: 'analytics',
  components: {
    // MainNavbar,
    // MainSidebar,
    // MainFooter,
  },
  data() {
    return {
      // sidebarItems: getSidebarItems(),
    };
  },
};
</script>

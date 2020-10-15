<!-- #SPDX-License-Identifier: MIT -->
<template>
  <footer class="main-footer d-flex p-2 px-3 bg-white border-top" style="position: fixed; left: 0;
  bottom: 0;
  width: 100%;
  text-align: center;
  z-index: 1001;">
    <div :class="[contained ? 'container' : 'container-fluid']">
      <div class="row" style="margin-top: 4px;">
        <ul class="nav" style="margin: 0px auto 0px auto;">
          <li v-for="(item, idx) in menuItems" :key="idx" class="nav-item">
            <d-link class="nav-link" :href="item.to">{{ item.title }}</d-link>
          </li>
        </ul>
        <!-- <span class="copyright ml-auto my-auto mr-2">{{ copyright }}</span> -->
      </div>
    </div>
  </footer>
</template>

<script>
const defaultMenuItems = [{
  title: 'Augur',
  to: 'http://augurlabs.io',
}, {
  title: 'CHAOSS',
  to: 'https://chaoss.community',
}, {
  title: 'Augur Documentation',
  to: 'https://oss-augur.readthedocs.io',
}, {
  title: 'Submit an Issue',
  to: 'https://github.com/chaoss/augur/issues/new/choose',
}];
export default {
  name: 'main-footer',
  props: {
    /**
       * The footer menu items.
       */
    menuItems: {
      type: Array,
      default() {
        return defaultMenuItems;
      },
    },
    /**
       * The copyright information.
       */
    copyright: {
      type: String,
      default: 'Copyright © 2018 DesignRevision',
    },
    /**
       * Whether the footer should be wrapped in a container, or not.
       */
    contained: {
      type: Boolean,
      default: true,
    },
  },
};
</script>

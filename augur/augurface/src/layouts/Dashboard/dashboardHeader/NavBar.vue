<!-- #SPDX-License-Identifier: MIT -->
<template>
  <vue-position-sticky>
    <div id="NavBar">
      <div class="nav-links">
        <nav-link v-for="link in links" :key="link.path" v-bind="link" />
      </div>
      <div class="buttons">
        <aug-icon-button iconClass="fas fa-bars" :circular="true" @click.stop="toggleSidePanel" />
        <aug-icon-button iconClass="fas fa-user" :circular="true" v-show="isLoggedIn"/>
        <img src="../../../assets/slackbutton.png" alt="sign in with slack" class="slack-button" v-show="!isLoggedIn"/>
      </div>
      <transition name="slide-right">
        <side-panel v-show="isSidePanelOpen" class="settings-panel" v-click-outside="closeSidePanel" ref="sidePanel" @darkClick="closeSidePanel">
          <settings-panel />
        </side-panel>
      </transition>
    </div>
  </vue-position-sticky>
</template>

<script>
import NavLink from "./NavLink.vue";
import AugIconButton from "../../../components/BaseComponents/AugIconButton.vue";
import SidePanel from "../../../components/SidePanels/SidePanel.vue";
import ClickOutside from "vue-click-outside";
import SettingsPanel from "../../../components/SidePanels/SettingsPanel.vue";
import { mapGetters } from "vuex";

export default {
  name: "NavBar",
  props: {
    links: {
      type: Array,
      required: false
    }
  },
  components: {
    NavLink,
    AugIconButton,
    SidePanel, 
    SettingsPanel
  },
  data() {
    return {
      isSidePanelOpen: false
    };
  },
  computed: {
    ...mapGetters("userModule", ["isLoggedIn"])
  }, 
  methods: {
    toggleSidePanel() {
      if (this.isSidePanelOpen) {
        this.isSidePanelOpen = false;
        this.$refs.sidePanel.fadeOut();
      }
      else {
        this.isSidePanelOpen = true;
        this.$refs.sidePanel.fadeIn();
      }
    }, 
    closeSidePanel() {
      this.$refs.sidePanel.fadeOut();
      this.isSidePanelOpen = false;
    }, 
    openSidePanel() {
      this.$refs.sidePanel.fadeIn();
      this.isSidePanelOpen = true;
    }
  }, 
  directives: {
    ClickOutside
  }
};
</script>

<style scoped>
#NavBar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: white;
  padding-top: 0rem;
  box-shadow: 0 10px 10px 0 var(--grey);
  z-index: 20;
  position: relative;
  border-bottom: 1px solid var(--grey);
}

.nav-links {
  display: flex;
  width: 800px;
}

.buttons {
  display: flex;
  align-items: center;
  justify-content: space-evenly;
}

.buttons > * {
  margin-right: .5rem;
}

.settings-panel {
  position: absolute;
  bottom: -100vh;
  right: 0;
}

.slack-button {
  width: 10rem;
  border-radius: .2rem;
  background-color: var(--grey);
  transition: box-shadow .3s ease;
}

.slack-button:hover {
  box-shadow: 0 0 3px 0 var(--grey);
  cursor: pointer;
}

.slide-right-enter-active,
.slide-right-leave-active {
  transition: transform 0.3s ease;
}

.slide-right-enter,
.slide-right-leave-to {
  transform: translateX(400px);
}

.slide-right-enter-to,
.slide-right-leave {
  transform: translateX(0px);
}
</style>
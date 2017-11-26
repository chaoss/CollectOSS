<template>
  <div>
    <ghdata-header></ghdata-header>
    <div class="content">
      <sidebar-controls></sidebar-controls>
      <ghdata-cards></ghdata-cards>
    </div>
  </div>
</template>

<script>

import GHDataHeader from './GHDataHeader.vue'
import SidebarControls from './SidebarControls.vue'
import GHDataCards from './GHDataCards.vue'

module.exports = {
  components: {
    'ghdata-header': GHDataHeader,
    SidebarControls,
    'ghdata-cards': GHDataCards
  }
}

</script>
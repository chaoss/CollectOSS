<template>
  <div>
    <augur-header></augur-header>
    <div class="content">
      <main-controls></main-controls>
      <augur-cards></augur-cards>
    </div>
  </div>
</template>

<script>

import AugurHeader from './AugurHeader.vue'
import MainControls from './MainControls.vue'
import AugurCards from './AugurCards.vue'

module.exports = {
  components: {
    'augur-header': AugurHeader,
    MainControls,
    'augur-cards': AugurCards
  }
}

</script>
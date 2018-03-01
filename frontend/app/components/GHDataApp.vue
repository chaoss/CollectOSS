<template>
  <div>
    <ghdata-header></ghdata-header>
    <div class="content">
      <main-controls></main-controls>
      <ghdata-cards></ghdata-cards>
    </div>
  </div>
</template>

<script>

import GHDataHeader from './GHDataHeader.vue'
import MainControls from './MainControls.vue'
import GHDataCards from './GHDataCards.vue'

module.exports = {
  components: {
    'ghdata-header': GHDataHeader,
    MainControls,
    'ghdata-cards': GHDataCards
  }
}

</script>
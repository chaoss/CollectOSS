<template>
  <div>
    <augur-header></augur-header>
    <div class="content">
      <augur-cards></augur-cards>
    </div>
  </div>
</template>

<script>

import AugurHeader from './AugurHeader.vue'
import AugurCards from './AugurCards.vue'

module.exports = {
  components: {
    'augur-header': AugurHeader,
    'augur-cards': AugurCards
  }
}

</script>
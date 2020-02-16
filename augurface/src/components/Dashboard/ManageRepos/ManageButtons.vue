<template>
  <div id="ManageButtons">
      <div class="column">
          <aug-button text="Create Group" />
      </div>
      <div class="column">
          <aug-button text="Collapse All" @click="$emit('collapseAll')"/>
      </div>
  </div>
</template>

<script>
import AugButton from '../../BaseComponents/AugButton.vue';
export default {
    name: 'ManageButtons', 
    components: {
        AugButton
    }
}
</script>

<style>
#ManageButtons {
    width: 90%;
    max-width: 1200px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin: 0;
}
</style>
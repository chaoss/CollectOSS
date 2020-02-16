<template>
  <div id="AddRepositoryPopup">
      <aug-text-input text="git urls (comma seperated)" inputName="urls" />
      <aug-text-input text="group name (optional)" inputName="groupName" />
      <aug-button text="Add" />
  </div>
</template>

<script>
import AugTextInput from '../../BaseComponents/AugTextInput.vue';
import AugButton from '../../BaseComponents/AugButton';

export default {
    name: 'AddRepositoryPopup', 
    components: {
        AugTextInput, 
        AugButton
    }
}
</script>

<style>
    #AddRepositoryPopup {
        background-color: white;
        display: flex;
        flex-direction: column;
        justify-content: space-evenly;
        align-items: center;
        position: fixed;
        height: 70vh;
        top: 10vh;
        width: 90%;
        margin: auto;
    }
</style>
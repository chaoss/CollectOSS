<template>
<transition name="modal">
    <div class="modal-mask" :class="{'is-active':active}">
      <div class="modal-wrapper">
        <div class="modal-container">
          <div class="modal-header">
            <slot name="header">
              Issue Title: {{modal.issue_title}}
            </slot>
          </div>

          <div class="modal-body">
            <slot name="body">
              default body
            </slot>
          </div>

          <div class="modal-footer">
            <slot name="footer">
              default footer
              <button class="modal-default-button" @click.prevent="active=false">
                Return
              </button>
            </slot>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>
<script>
export default {
  data() {
    return {
      active: false,
      modal: false,
    }
  },
  methods: {
    show() {
      this.active = true;
      console.log('debug', this.active)
    }
  },
  created() {
    window.AugurApp.$on('toggleModal', (row) => {
      this.modal = row;
      this.show();
    });
  },
}
</script>
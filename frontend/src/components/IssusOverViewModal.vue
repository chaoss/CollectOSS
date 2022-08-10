<!-- #SPDX-License-Identifier: MIT -->
<template>
<transition name="modal">
    <div class="modal-mask" :class="{'is-active':active}">
      <div class="modal-wrapper">
        <div class="modal-container">
          <div class="modal-header">
            <slot name="header">
             Issue Detail
            </slot>
          </div>

          <div class="modal-body">
            <slot name="body">
               Title: {{modal.issue_title}} <br />
               Issue ID: {{modal.issue_id}}<br/>
               URL: <a v-bind:href="modal.html_url">{{modal.html_url}}</a><br/>
               Status: {{modal.status}}<br />
               Open Day: {{modal.open_day}} <br />
               Date: {{modal.date}}<br />
               Last Event Created at: {{modal.last_event_date}} <br/>
            </slot>
          </div>

          <div class="modal-footer">
            <slot name="footer">
              <div>
              <button class="modal-default-button" @click.prevent="active=false">
                Return
              </button>
              </div>
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
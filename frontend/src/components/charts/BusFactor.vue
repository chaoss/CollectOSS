<!-- #SPDX-License-Identifier: MIT -->
<template>
  <div ref="holder">
    <div class="textchart hidefirst invis">
      <h3>{{ title }}</h3>
      <table>
        <tr>
          <th>Best:</th>
          <td>{{ (values[0]) ? values[0].best : undefined }}</td>
        </tr>
        <tr>
          <th>Worst</th>
          <td>{{ (values[0]) ? values[0].worst : undefined }}</td>
        </tr>
      </table>
      <p> {{ chart }} </p>
    </div>
  </div>
</template>

<script>
  export default {
    props: ['source', 'citeUrl', 'citeText', 'title'],
    data() {
      return {
        values: []
      }
    },
    computed: {
      repo() {
        return this.$store.state.baseRepo
      },
      chart() {
        $(this.$el).find('.showme').addClass('invis');
        $(this.$el).find('.textchart').addClass('loader');
        if (this.repo) {
          window.AugurRepos[this.repo][this.source]().then((data) => {
            $(this.$el).find('.showme, .hidefirst').removeClass('invis');
            $(this.$el).find('.textchart').removeClass('loader');
            this.values = data;
          })
        }
      }
    }
  }
</script>

<!-- #SPDX-License-Identifier: MIT -->
<template>
   <section v-click-outside="">
      <div class="projectDropdown">
         <div class="cd-dropdown-wrapper">
      <a class="cd-dropdown-trigger"  @click="toggleNav" href="#0">{{ project }}</a>
      <nav class="cd-dropdown">
         <h2>Projects</h2>
         <a href="#0" class="cd-close">Close</a>
         <ul class="cd-dropdown-content">
            <li>
               <form class="projectDropdownForm cd-search">
                  <input type="search" placeholder="Search...">
               </form>
            </li>
            <li class="cd-divider">Projects</li>
            <li v-for="project in projects" class="has-children">
               <a @click="toggleSecNav" href="#0">{{ project }}</a>
               <ul class="cd-secondary-dropdown  invis">
                  <!-- <li class="go-back"><a href="#0">Menu</a></li>
                   <li class="see-all"><a href="#0">All Clothing</a></li>-->
                  <li class="has-children">
                     <a href="#0">Repos</a>

                     <ul class="is-hidden">
                        <!-- <li class="go-back"><a href="#0">Clothing</a></li>
                        <li class="see-all"><a href="#0">All Accessories</a></li> -->
                        <li v-for="repo in (repos[project])" class=""> <!--has-children-->
                           <a @click="toggleSelect" value="" href="#0">{{ repo.url }}</a>
                           <!-- <ul class="is-hidden">
                              <li class="go-back"><a href="#0">Accessories</a></li>
                              <li class="see-all"><a href="#0">All Benies</a></li>
                              <li><a href="#0">Caps &amp; Hats</a></li>
                           </ul> -->
                        </li>
                     </ul>
                  </li>
               </ul> <!-- .cd-secondary-dropdown -->
            </li> <!-- .has-children -->

            <li class="has-children">
               <!-- other list items here -->
            </li> <!-- .has-children -->

            <li class="has-children">
               <!-- other list items here -->
            </li> <!-- .has-children -->

            <li class="cd-divider">Groups</li>

            <li class="has-children">
               <a href="#0">Test Group</a>
            </li>
            <!-- other list items here -->

         </ul> <!-- .cd-dropdown-content -->
      </nav> <!-- .cd-dropdown -->
   </div> <!-- .cd-dropdown-wrapper -->
      </div>
   </section>
   

</template>

<script>
export default {

  components: {

  },
  data () { return {
    repos: {},
    projects: [],
    project: 'Twitter'
  }},
  directives: {
      'click-outside': {
        bind: function(el, binding, vNode) {
          if (typeof binding.value !== 'function') {
            const compName = vNode.context.name
            let warn = `[Vue-click-outside:] provided expression '${binding.expression}' is not a function, but has to be`
            if (compName) { warn += `Found in component '${compName}'` }
          }
          const bubble = binding.modifiers.bubble
          const handler = (e) => {
            if (bubble || (!el.contains(e.target) && el !== e.target)) {
              binding.value(e)
            }
          }
          el.__vueClickOutside__ = handler
          document.addEventListener('click', handler)
        },
        unbind: function(el, binding) {
          document.removeEventListener('click', el.__vueClickOutside__)
          el.__vueClickOutside__ = null
        }
      }
    },
  methods: {
   toggleSelect(e) {

   },
   toggleSecNav(){
       var navIsVisible = ( !$('.cd-secondary-dropdown').hasClass('invis') ) ? true : false;
       if (navIsVisible) {
         console.log("hiding")
         $('.cd-secondary-dropdown').addClass('invis')
       } else {
         console.log("unhiding")
         // $('.cd-secondary-dropdown').one('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend',function(){
           // $('.has-children ul').addClass('is-hidden');
           // $('.move-out').removeClass('move-out');
           // $('.is-active').removeClass('is-active');
           $('.cd-secondary-dropdown').removeClass('invis')
         // }); 
         
       }
   },
   toggleNav(){
       var navIsVisible = ( !$('.cd-dropdown').hasClass('dropdown-is-active') ) ? true : false;
       $('.cd-dropdown').toggleClass('dropdown-is-active', navIsVisible);
       $('.cd-dropdown-trigger').toggleClass('dropdown-is-active', navIsVisible);
       if( !navIsVisible ) {
         $('.cd-dropdown').one('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend',function(){
           $('.has-children ul').addClass('is-hidden');
           $('.move-out').removeClass('move-out');
           $('.is-active').removeClass('is-active');
         }); 
       }
   },
    onRepo (e) {
      this.$store.commit('setRepo', {
        githubURL: e.target.value
      })
    },
    onGitRepo (e) {
      let first = e.url.indexOf(".")
      let last = e.url.lastIndexOf(".")
      let domain = null
      let owner = null
      let repo = null
      let extension = false

      if (first == last){ //normal github
        domain = e.url.substring(0, first)
        owner = e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'))
        repo = e.url.slice(e.url.lastIndexOf('/') + 1)
      } else if (e.url.slice(last) == '.git'){ //github with extension
        domain = e.url.substring(0, first)
        extension = true
        owner = e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'))
        repo = e.url.substring(e.url.lastIndexOf('/') + 1, e.url.length - 4)
      } else { //gluster
        domain = e.url.substring(first + 1, last)
        owner = null //e.url.substring(e.url.indexOf('/') + 1, e.url.lastIndexOf('/'))
        repo = e.url.slice(e.url.lastIndexOf('/') + 1)
      }
      this.$store.commit('setRepo', {
        gitURL: e.url
      })

      this.$store.commit('setTab', {
        tab: 'git'
      })

      this.$router.push({
        name: 'git',
        params: {repo: e.url}
      })
    },
    getDownloadedRepos() {
      this.downloadedRepos = []
      window.AugurAPI.getDownloadedGitRepos().then((data) => {
        $(this.$el).find('.spinner').removeClass('loader')
        $(this.$el).find('.spinner').removeClass('relative')
        this.repos = window._.groupBy(data, 'project_name')

        this.projects = Object.keys(this.repos)
         // projects.forEach((project) => {
         //    repos[project].forEach((repo) => {
         //       repo.name = repo.url.split
         //    })
         // })
      })
    },
    btoa(s) {
      return window.btoa(s)
    }
  },
  mounted() {
    this.getDownloadedRepos()
  } 
};
// jQuery(document).ready(function($){
//   //open/close mega-navigation
//   $('.cd-dropdown-trigger').on('click', function(event){
//     event.preventDefault();
//     toggleNav();
//   });

//   //close meganavigation
//   $('.cd-dropdown .cd-close').on('click', function(event){
//     event.preventDefault();
//     toggleNav();
//   });

//   //on mobile - open submenu
//   $('.has-children').children('a').on('click', function(event){
//     //prevent default clicking on direct children of .has-children 
//     event.preventDefault();
//     var selected = $(this);
//     selected.next('ul').removeClass('is-hidden').end().parent('.has-children').parent('ul').addClass('move-out');
//   });

//   //on desktop - differentiate between a user trying to hover over a dropdown item vs trying to navigate into a submenu's contents
//   var submenuDirection = ( !$('.cd-dropdown-wrapper').hasClass('open-to-left') ) ? 'right' : 'left';
//   $('.cd-dropdown-content').menuAim({
//         activate: function(row) {
//           $(row).children().addClass('is-active').removeClass('fade-out');
//           if( $('.cd-dropdown-content .fade-in').length == 0 ) $(row).children('ul').addClass('fade-in');
//         },
//         deactivate: function(row) {
//           $(row).children().removeClass('is-active');
//           if( $('li.has-children:hover').length == 0 || $('li.has-children:hover').is($(row)) ) {
//             $('.cd-dropdown-content').find('.fade-in').removeClass('fade-in');
//             $(row).children('ul').addClass('fade-out')
//           }
//         },
//         exitMenu: function() {
//           $('.cd-dropdown-content').find('.is-active').removeClass('is-active');
//           return true;
//         },
//         submenuDirection: submenuDirection,
//     });

//   //submenu items - go back link
//   $('.go-back').on('click', function(){
//     var selected = $(this),
//       visibleNav = $(this).parent('ul').parent('.has-children').parent('ul');
//     selected.parent('ul').addClass('is-hidden').parent('.has-children').parent('ul').removeClass('move-out');
//   }); 

  

//   //IE9 placeholder fallback
//   //credits http://www.hagenburger.net/BLOG/HTML5-Input-Placeholder-Fix-With-jQuery.html
//   if(!Modernizr.input.placeholder){
//     $('[placeholder]').focus(function() {
//       var input = $(this);
//       if (input.val() == input.attr('placeholder')) {
//         input.val('');
//         }
//     }).blur(function() {
//       var input = $(this);
//         if (input.val() == '' || input.val() == input.attr('placeholder')) {
//         input.val(input.attr('placeholder'));
//         }
//     }).blur();
//     $('[placeholder]').parents('form').submit(function() {
//         $(this).find('[placeholder]').each(function() {
//         var input = $(this);
//         if (input.val() == input.attr('placeholder')) {
//           input.val('');
//         }
//         })
//     });
//   }
// });
</script>
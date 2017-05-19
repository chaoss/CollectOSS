exports.config =
  # See http://brunch.io/#documentation for docs.
  files:
    javascripts:
      joinTo:
        'js/app.js': /^app/
        'js/vendor.js': /^(?!app)/
    stylesheets:
      joinTo: 'app.css'
    templates:
      joinTo: 'js/app.js'
  plugins:
    order: ['riot-brunch', 'babel-brunch']
    babel:
      presets: ['es2015-riot']

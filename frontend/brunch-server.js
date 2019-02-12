const express = require('express');
const proxy   = require('express-http-proxy');
const app     = express();

function augur_log(str) {
  console.log("\033[0;33maugur-frontend\033[0;0m: " + str);
}




app.use('/static', express.static(__dirname + '/public'));

app.use('*', proxy('localhost:5000', {
  proxyReqPathResolver: function(req) {
    return req.originalUrl
  }
}));


module.exports = (config, callback) => {
  app.listen(config.port, function () {
    augur_log(`listening on http://${config.hostname}:${config.port}`)
    callback()
  });
  return app;
};
const express = require('express');
const proxy   = require('express-http-proxy');
const app     = express();

function ghdata_log(str) {
  console.log("\033[0;33mghdata-frontend\033[0;0m: " + str);
}

app.get('/', function(req, res) {
    res.sendFile(__dirname + '/public/index.html')
})
app.use('/api*', proxy('localhost:5000', {
  proxyReqPathResolver: function(req) {
    ghdata_log('API call, proxy http://localhost:5000' + req.originalUrl)
    return req.originalUrl
  }
}));
app.use('/static/', express.static(__dirname + '/public'));

module.exports = (config, callback) => {
  app.listen(config.port, function () {
    ghdata_log(`listening on http://${config.hostname}:${config.port}`)
    callback()
  });
  return app;
};
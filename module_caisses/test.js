var opener = require('./node_modules/opener')
var cp = require('child_process')


module.exports = {
 afficherClan: function (myclan)
{
  opener('./'+myclan+'.html')

  var chrome = cp.spawn('chromium')

  chrome.stdout.on('data', function(data){
    console.log(data.toString())
  })

  chrome.stderr.on('data', function(data){
    console.error(data.toString())
  })
}

};

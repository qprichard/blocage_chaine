
function HTTPRequest()
{
var xhttp = new XMLHttpRequest();
xhttp.open("GET", "http://blackaquilius.alwaysdata.net/", true);
xhttp.send();
console.log(xhttp.responseText)
}

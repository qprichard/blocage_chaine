let ws = new WebSocket('ws://localhost:9292/events');


ws.addEventListener('message', function(data){
  let message = data.data;
  //console.log('CARD ID', message)
  message = message.substr(13,message.lenth);
  console.log(message);
  $.ajax
    ({
        type: "POST",
        //the url where you want to sent the userName and password to
        url: 'http://crichard.fr/endpoint',
        dataType: 'json',
        async: true,
        //json object to sent to the authentication url
        data: {"message": message},
        success: function (data) {
          clan = data.clan;
          console.log(clan)
          if(clan=='jew') $("#photo").attr('src',"../src/"+clan+".jpg")
          else $("#photo").attr('src',"../src/"+clan+".png")


        }
    })
});

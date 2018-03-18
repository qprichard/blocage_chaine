
require('./config.js')
const myClan =require('./test')
const payutc = require('./payutc.js');
payutc.config.setAppKey(APP_KEY);
mySqlClient = SQLConnection();
ispresent = 1;
winningclan = 'italian'

payutc.login.payuser({login:USERNAME, password:PASSWORD, callback: function(){init()}});


function init()
{
  const WebSocket = require('ws');
  let ws = new WebSocket('ws://localhost:9292/events');

  ws.addEventListener('message', function(data){
  	let message = data.data;
  	//console.log('CARD ID', message)
    message = message.substr(13,message.lenth);
    console.log(message);
    getInformation(mySqlClient, message, function(err, data){
      console.log(ispresent)


      if(!ispresent) {
       getUserInfo(message, 'login', function(err, data){
         console.log(data)
        clan = insertIntoBdd(mySqlClient, data[0]['tag'], data[0]['username'], data[0]['user_id'], data[0]['id'])

       });
      //  data = getUserInfo(message, 'login');

        //insertIntoBdd(mySqlClient, message, login, usr_id, wallet);
      }
    });
   });
}


function getUserInfo(uid, type, callback){

    console.log("Getting "+uid+' informations');

    payutc.user.getUserInfo({queryString: uid, wallet_config:1, callback: function(response){
      let data = JSON.parse(response);
      if(data.error) return console.log(data.error);
      return callback(null, data);

    }
    });
}

function SQLConnection(){
  try {
    var mysql = require('mysql');
    var mySqlClient = mysql.createConnection({
      host  : BDD_HOST,
      user : BDD_USERNAME,
      password  : BDD_PASSWORD,
      database  : BDD
    });
  } catch (e) {
    console.log("erreur de connection")

  } finally {
      console.log("Connection établie.")
      return mySqlClient;
  }
}

function getInformation(mySqlClient, uid, callback){
  var selectQuery = 'Select * from users where id_badge="'+uid+'"';
  //ispresent = 0;
  mySqlClient.query(
    selectQuery,
    function select(error, results, fields){

      if(results.length>0)
      {
      ispresent = 1
      console.log ('Cette personne est dans la base');
      getWin(mySqlClient, function(err, data){
          if(data[0]['name']==results[0]['clan']) updatePoints(mySqlClient, OLD_MEMBER_PTS, results[0]['clan'])
          else updatePoints(mySqlClient, LOOSER_MEMBER_PTS, results[0]['clan'])

      })


      }
      else
      {
        ispresent = 0
         console.log ('Cette personne n est pas dans la base');


       }
        //mySqlClient.end();
        callback(null, ispresent)
    }

  );

}

function insertIntoBdd(mySqlConnection, uid, login, usr_id, wallet)
{
  var clan_tab = ['peaky', 'jew', 'italian']
  var randomIndex = Math.floor(Math.random()*clan_tab.length);
  var clan = clan_tab[randomIndex];
  var insertQuery = "insert into users (id_badge, login, usr_id, wallet, clan) values('"+uid+"','"+login+"','"+usr_id+"','"+wallet+"','"+clan+"')";

  mySqlClient.query(
    insertQuery,
    function (err, result){
      if(err) throw err;
      console.log("1 record inserted");

      updatePoints(mySqlConnection, NEW_MEMBER_PTS, clan)
    }
  );

  return clan;
}

function updatePoints(mySqlConnection, pts, clan)
{
  myClan.afficherClan(clan)
  var updateData = "update points set pts = pts+"+pts+" where name='"+clan+"';"
  mySqlClient.query(
    updateData,
    function(err,result){
      if(err) throw err;
      console.log("points mis à jour")
    }

  );
}

function getWin(mySqlConnection, callback)
{
  var selectData = "select name from points where pts = (select max(pts) from points)"
  mySqlClient.query(
    selectData,
    function (err, result){
      callback(null, result)
    }
  );
}

import mysql.connector
import MySQLdb as db
from mysql.connector import errorcode
import mdp
import csv
import requests
import json
import urllib
import urllib.parse


headers = {
    'Host': 'api.nemopay.net',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': 'application/json',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://admin.nemopay.net/',
    'Content-Type': 'application/json',
    'Content-Length': '91',
    'Origin': 'https://admin.nemopay.net',
    'Connection': 'keep-alive',
}
params = (
    ('system_id', 'payutc'),
    ('app_key', mdp.APP_KEY),
    #('sessionid', 'wq6g9czs7gfjdt109418b2tix56w9tv8'),
)

def MySqlConnection():
    try:
      cnx = mysql.connector.connect(user=mdp.BDD_USER, password=mdp.BDD_PASSWORD, host=mdp.BDD_HOST, database=mdp.BDD)

    except mysql.connector.Error as err:
      if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
        print("Something is wrong with your user name or password")
      elif err.errno == errorcode.ER_BAD_DB_ERROR:
        print("Database does not exist")
      else:
        print(err)
    else:
        print("connecté")
        return cnx

def MySqlConnection2():
    try:
        connection = db.Connection(host=mdp.BDD_HOST,
                                       user=mdp.BDD_USER, passwd=mdp.BDD_PASSWORD, db=mdp.BDD)



    except Exception as e:
        print (e)

    finally:
        print('connecté à la bdd')
        return connection


def MySqlDeconnection(cnx):
    cnx.close()
    print("Connexion mySQL terminée")


def UsersInformation(cnx):
    params = "Select * from users where added = 0 and admin = 0"
    cursor = cnx.cursor()
    cursor.execute(params)
    rows = cursor.fetchall()
    with open('nouv_liste.csv', 'w') as myfile:
        myfile.write('')
    with open('nouv_liste.csv', 'a') as myfile:
        for row in rows:
            print('{0} : {1} - {2} - {3} - {4} - {5} - {6}'.format(row[0], row[1], row[2], row[3], row[4], row[5], row[6]))
            myLine = str(row[1])+';'+str(row[2])+';'+str(row[3])+';'+str(row[5])+'\n'
            myfile.write(myLine)
            UpdateAdded(cnx, row[1])

def UpdateAdded(cnx, login):
    params = "Update users set added = 1 where login ='"+str(login)+"';"
    cursor = cnx.cursor()
    cursor.execute(params)
    cnx.commit()



def getWin(cnx):
    params = "select name from points where pts = (select max(pts) from points)"
    cursor = cnx.cursor()
    cursor.execute(params)
    rows = cursor.fetchall()
    for row in rows:
        return row[0]

def insertAdmin(cnx):
    sessionid = loginCas2(mdp.USERNAME, mdp.PASSWORD)['sessionid']
    with open('liste_admin.csv', 'rt') as myfile :
        spamreader = csv.reader(myfile, delimiter=';', quotechar='|')
        for row in spamreader:
            if(row[0]!=''):
                data = getUserInfo(str(row[0]),'rien', sessionid)
                id_badge = data['tag']
                login = data['username']
                usr_id = data['user_id']
                wallet = data['id']
                myInsert = "insert into users (id_badge, login, usr_id, wallet, admin, clan) values ('"+str(id_badge)+"','"+str(login)+"','"+str(usr_id)+"','"+str(wallet)+"',1,'peaky');"
                cursor = cnx.cursor()
                cursor.execute(myInsert)
                cnx.commit()


def loginCas2(username,password):
    myheaders = {
                'Content-Type': 'application/json',
                'Nemopay-Version': '2017-12-15'
    }

    params = (
        ('system_id', 'payutc'),
        ('app_key', mdp.APP_KEY),
        #('sessionid', 'vc4zyvwjkbwxxfo9zaowyl0d7e4yx5lh'),
    )
    service = 'http://localhost/nemopay-mini-cli/login'
    casurl = requests.post('https://api.nemopay.net/services/ROSETTINGS/getCasUrl', headers=myheaders, params=params)
    casurl = json.loads(casurl.text)

    headerscas = {
		'Content-type': 'application/x-www-form-urlencoded',
		'Accept': 'text/plain',
		'User-Agent':'python'
	}
    #Permet d'encoder pour une connexion automatique
    paramscas = urllib.parse.urlencode({
		'service': service,
		'username': username,
		'password': password
	})

    response = requests.post(casurl+'/v1/tickets/', headers=headerscas, params=paramscas)
    location = response.headers['location']
    tgt = location[location.rfind('/')+1:]

    response = requests.post(casurl+'/v1/tickets/'+tgt, headers=headerscas, params=paramscas)
    st = response.text

    data = '{"ticket":"'+st+'","service":"'+service+'"}'
    response = requests.post('https://api.nemopay.net/services/MYACCOUNT/loginCas2', headers=headers, params=params, data=data)

    if response.status_code == 200:
        print("logged in via CAS as "+response.json()['username'])

    return response.json()

def getUserInfo(info, type, sessionid):

    print("Getting " + info + ' '+ type )

    myheaders = {
    		'Content-Type': 'application/json',
    		'Nemopay-Version': '2017-12-15',
    }

    params = (
		('system_id', 'payutc'),
        ('app_key', mdp.APP_KEY),
		('sessionid', sessionid),

	)
    data = '{"queryString":"'+str(info)+'","wallet_config":1}'
    response = requests.post('https://api.nemopay.net/services/GESUSERS/walletAutocomplete', headers=myheaders, params=params, data=data)
    print(info+' '+type+' getted')
    return response.json()[0]

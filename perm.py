import csv
import sys, getopt, os.path
import requests
import json
import urllib
import urllib.parse
import time
import mdp
import random
from difflib import unified_diff
from threading import Thread
from bdd import MySqlConnection, MySqlDeconnection, UsersInformation, getWin

global thread_tab
global winningclan
thread_tab=[]
winningclan ='peaky'
class Bloqueur(Thread):
    def __init__(self, username, blockingTime, unblockingTime, sessionid, fundationid, reason, clan):
        Thread.__init__(self)
        self.username = username
        self.blockingTime = blockingTime
        self.unblockingTime = unblockingTime
        self.sessionid = sessionid
        self.fundationid = fundationid
        self.reason = reason
        self.clan = clan
    def run(self):
        usr_id = getUserInfo(self.username, 'usrid', self.sessionid)
        wallet = getUserInfo(self.username, 'wallet', self.sessionid)
        loopingblock(self.fundationid, usr_id, wallet, self.reason, self.sessionid, self.blockingTime, self.unblockingTime, self.clan)


class Main_Thread(Thread):
    def __init__(self, filename, blockingTime, unblockingTime, sessionid, fundationid, reason):
        Thread.__init__(self)
        self.filename = filename
        self.blockingTime = blockingTime
        self.unblockingTime = unblockingTime
        self.sessionid = sessionid
        self.fundationid = fundationid
        self.reason = reason

    def run(self):
        while True:
            cnx = MySqlConnection()
            UsersInformation(cnx)
            MySqlDeconnection(cnx)
            print("Acces à la base de donnée pour reccuperer les nouveaux utilisateurs")
            compareCSV('liste2.csv', 'nouv_liste.csv', self.filename)
            creatingThread(self.filename, self.blockingTime, self.unblockingTime, self.sessionid, self.fundationid, self.reason)
            time.sleep(20)

class Power_Thread(Thread):
    def __init__(self):
        Thread.__init__(self)
    def run(self):
        global winningclan

        while True:
            cnx = MySqlConnection()
            winningclan = getWin(cnx)
            MySqlDeconnection(cnx)
            print("le clan gagnant est "+ winningclan)
            time.sleep(10)


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


def compareCSV(csvfile, newcsvfile, fileToAdd):
    with open(str(csvfile), 'r') as t1, open(str(newcsvfile), 'r') as t2:
        fileone = t1.readlines()
        filetwo = t2.readlines()

    t1.close()
    t2.close()

    with open(str(csvfile), 'a') as outFile, open(str(fileToAdd), 'w') as new:
        for line in filetwo:
            if line not in fileone:
                outFile.write(line)
                new.write(line)
                print('user ajouté')


#fonction pour bloquer quelqu'un à partir d'un usrid et d'un wallet sur une fondation donnee
def block_User(usr_id, wallet, fundationid, reason, sessionid):
    blocked_id = 0
    params = (
        ('system_id', 'payutc'),
        ('app_key', mdp.APP_KEY),
        ('sessionid', str(sessionid)),
    )
    data='{"usr_id":'+str(usr_id)+',"wallet":'+str(wallet)+',"raison":"'+str(reason)+'","fun_id":'+str(fundationid)+',"date_fin":"2019-03-08T22:59:00.000Z"}'

    response = requests.post('https://api.nemopay.net/services/BLOCKED/block', headers=headers, params=params, data=data)

    #reccupere le blo_id de la personne
    data='{"fun_id":'+str(fundationid)+'}'
    response = requests.post('https://api.nemopay.net/services/BLOCKED/getAll', headers=headers, params=params, data=data)
    json_data = json.loads(response.text)

    for key, value in json_data.items():
        if(value['wallet_id']==wallet):
            blocked_id = value['blo_id']
            print(value['login'],' ',value['blo_id'],'blocked')

    return blocked_id

#fonction débloquant un user à partir du blo_id et du fun_id
def unblock_User(fundationid, blo_id, sessionid):


    params = (
        ('system_id', 'payutc'),
        ('app_key', mdp.APP_KEY),
        ('sessionid', str(sessionid)),
    )


    data='{"fun_id":'+str(fundationid)+',"blo_id":'+str(blo_id)+'}'
    response = requests.post('https://api.nemopay.net/services/BLOCKED/remove', headers=headers, params=params, data=data)
    print("user unblocked")

#login Cas
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

#permet d'obtenir les infos sur un user en donnant login, badge ou wallet
#Type permet de definir le type d'info en retour (username, wallet, usrid, tag)
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

    if(type == 'username'):
        return response.json()[0]['username']
    if(type == 'wallet'):
        return response.json()[0]['id']
    if(type == 'usrid'):
        return response.json()[0]['user_id']
    if(type == 'tag'):
        return response.json()[0]['tag']

#bloque et débloque en boucle avec un temps de bloquage et de débloquage
def loopingblock(fundation, usrid, wallet, reason, sessionid, blockingTime, unblockingTime, clan):
    block = 0

    while True:
        global winningclan
        if(clan!=winningclan):
            if(block!=0):
                unblock_User(fundation, block, sessionid)
                block = 0
                time.sleep(unblockingTime)
            else:
                block = block_User(usrid, wallet, fundation, reason, sessionid)
                time.sleep(blockingTime)
        else:
            if(block!=0):
                unblock_User(fundation, block, sessionid)
                block = 0

#definit date/heure etc /!\ INUTILISE /!\
def setBlockend(number, type):
    t = time.localtime()

    if(type=='year'): tyear = t.tm_year+number
    else : tyear = t.tm_year
    if(type=='month'): tmonth = (t.tm_mon+number)%12
    else : tmonth = t.tm_mon
    if(type=='day'): tday = (t.tm_mday+number)%31
    else : tday = t.tm_mday
    if(type=='hour'): thour = (t.tm_hour+number)%24
    else : thour = t.tm_hour
    if(type=='min'): ttmin = (t.tm_min+number)%60
    else : ttmin = t.tm_min
    if(type=='sec'): tsec = (t.tm_sec+number)%60
    else : tsec = t.tm_sec





    year = str(tyear)
    if tmonth<10 : month = '0'+str(tmonth)
    else:  month = str(tmonth)
    if tday<10 : day = '0'+str(tday)
    else:  day = str(tday)
    if thour<10 : hour = '0'+str(thour)
    else:  hour = str(thour)
    if ttmin<10 : tmin = '0'+str(ttmin)
    else:  tmin = str(ttmin)
    if tsec<10 : sec = '0'+str(tsec)
    else:  sec = str(tsec)


    mytime =year+'-'+month+'-'+day+'T'+hour+':'+tmin+':'+sec+'.000Z'

    return mytime


#crée un thread par personne a bloquer
def creatingThread(inputfile, blockingTime, unblockingTime,  sessionid, fundationid, reason):
    print("enter in thread creation")


    with open(inputfile, 'rt') as csvfile:
        print("CSV file opened")
        spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
        for row in spamreader:
            if(row[0]!=''):
                thread_tab.append(Bloqueur(str(row[0]), blockingTime, unblockingTime, sessionid, fundationid, reason, str(row[3])))
                print(row[0])


    for i in range(len(thread_tab)):
        if(thread_tab[i].isAlive()==0):
            thread_tab[i].start()
            print("thread "+str(i)+"started")
    """for i in range(len(thread_tab)):
        if(thread_tab[i].isAlive()==1):
            thread_tab[i].join()"""


def main(argv):

    filename = str(sys.argv[1])
    fundationid = str(sys.argv[2])
    reason = str(sys.argv[3])
    blockingTime = int(sys.argv[4])
    unblockingTime = int(sys.argv[5])

    data = loginCas2(mdp.USERNAME, mdp.PASSWORD)
    sessionid = data['sessionid']

    #usr_id = getUserInfo('mmarchan', 'usrid', sessionid)
    #wallet = getUserInfo('mmarchan', 'wallet', sessionid)
    #creatingThread(filename, blockingTime, unblockingTime, str(sessionid), fundationid, reason)


    mt = Main_Thread(filename, blockingTime, unblockingTime, str(sessionid), fundationid, reason)
    pt = Power_Thread()
    mt.start()
    pt.start()


if __name__ == "__main__":
	main(sys.argv[1:])

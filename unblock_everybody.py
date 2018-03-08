import csv, json
import sys, getopt, os.path
import requests
import json
import urllib
import urllib.parse
import time
import mdp
import random
from threading import Thread

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


def unblock(fundationid, sessionid):
    params = (
        ('system_id', 'payutc'),
        ('app_key', mdp.APP_KEY),
        ('sessionid', str(sessionid)),
    )

    data='{"fun_id":'+str(fundationid)+'}'
    response = requests.post('https://api.nemopay.net/services/BLOCKED/getAll', headers=headers, params=params, data=data)
    json_data = json.loads(response.text)

    for key, value in json_data.items():
            blocked_id = value['blo_id']
            data='{"fun_id":'+str(fundationid)+',"blo_id":'+str(blocked_id)+'}'
            response = requests.post('https://api.nemopay.net/services/BLOCKED/remove', headers=headers, params=params, data=data)
            print(value['login'],' ',value['blo_id'], ' unblocked')

    #data='{"fun_id":'+str(fundationid)+',"blo_id":'+str(blo_id)+'}'
    #response = requests.post('https://api.nemopay.net/services/BLOCKED/remove', headers=headers, params=params, data=data)
    #print("user unblocked")
def setBackup(fundationid, sessionid):
    params = (
        ('system_id', 'payutc'),
        ('app_key', mdp.APP_KEY),
        ('sessionid', str(sessionid)),
    )

    data='{"fun_id":'+str(fundationid)+'}'
    response = requests.post('https://api.nemopay.net/services/BLOCKED/getAll', headers=headers, params=params, data=data)
    json_data = json.loads(response.text)
    with open("backup.json", "w") as outfile:
        json.dump(json_data, outfile, indent = 4)
        print('Backup créé')

def blockPreviousUsers(fundationid, sessionid):
    json_data = open("backup.json").read()
    data = json.loads(json_data)

    for key, value in data.items():

        usrid = getUserInfo(value['login'], 'usrid', sessionid)
        wallet = getUserInfo(value['login'], 'wallet', sessionid)
        reason = str(value['blo_raison'])
        end = str(value['blo_removed'])
        block_User(usrid,wallet,reason,end,fundationid, sessionid)
        print(value['login'],' ',usrid,' ',wallet,' ',reason,' ', end, ' blocked')

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

def block_User(usr_id, wallet, reason, end, fundationid, sessionid):
    #blocked_id = 0

    params = (
        ('system_id', 'payutc'),
        ('app_key', mdp.APP_KEY),
        ('sessionid', str(sessionid)),
    )

    #2019-03-05T22:59:00.000Z
    #ajoute la personne a bloquer
    #data = '{"usr_id":'+str(usr_id)+',"wallet":'+str(wallet)+',"raison":"test Payutc. Merci de patienter 1 à 2 minutes","fun_id":'+str(fundationid)+',"date_fin":"2019-04-05T22:59:00.000Z"}'
    data='{"usr_id":'+str(usr_id)+',"wallet":'+str(wallet)+',"raison":"'+str(reason)+'","fun_id":'+str(fundationid)+',"date_fin":"'+str(end)+'"}'


    response = requests.post('https://api.nemopay.net/services/BLOCKED/block', headers=headers, params=params, data=data)



def main(argv):
    parameter = str(sys.argv[1])

    data = loginCas2(mdp.USERNAME, mdp.PASSWORD)
    sessionid = data['sessionid']
    fundationid = 2

    if(parameter == "backup"):
        setBackup(fundationid, sessionid)
    if(parameter == "unblock"):
        unblock(fundationid, sessionid)
        blockPreviousUsers(fundationid, sessionid)





if __name__ == "__main__":
	main(sys.argv[1:])

import csv
import sys, getopt, os.path
import requests
import json
import urllib
import urllib.parse
import time
import mdp



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





def block_User(usr_id, wallet, fundationid, sessionid):
    blocked_id = 0

    params = (
        ('system_id', 'payutc'),
        ('app_key', mdp.APP_KEY),
        ('sessionid', str(sessionid)),
    )


    #ajoute la personne a bloquer
    data = '{"usr_id":'+str(usr_id)+',"wallet":'+str(wallet)+',"raison":"fils de ta maman","fun_id":'+str(fundationid)+',"date_fin":"2019-03-05T22:59:00.000Z"}'
    response = requests.post('https://api.nemopay.net/services/BLOCKED/block', headers=headers, params=params, data=data)


    #reccupère le blo_id de la personne
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
    if(type == 'username'):
        return response.json()[0]['username']
    if(type == 'wallet'):
        return response.json()[0]['id']
    if(type == 'usrid'):
        return response.json()[0]['user_id']
    if(type == 'tag'):
        return response.json()[0]['tag']

def loopingblock(fundation, usrid, wallet, sessionid, sleepingTime):
    block = 0
    while True:
        if(block!=0):
            unblock_User(fundation, block, sessionid)
        else:
            block = block_User(usrid, wallet, fundation, sessionid)
        time.sleep(sleepingTime)


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









def main(argv):

    data = loginCas2(mdp.USERNAME, mdp.PASSWORD)
    sessionid = data['sessionid']
    usr_id = getUserInfo('mmarchan', 'usrid', sessionid)
    wallet = getUserInfo('mmarchan', 'wallet', sessionid)
    fundationid = 2

    loopingblock(fundationid, usr_id, wallet, sessionid, 20)













if __name__ == "__main__":
	main(sys.argv[1:])

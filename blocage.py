import csv
import sys, getopt, os.path
import requests
import json
import urllib
import time

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
    ('app_key', 'ENTER YOUR APP_KEY HERE'),
    ('sessionid', 'vc4zyvwjkbwxxfo9zaowyl0d7e4yx5lh'),
)



def block_User(usr_id, wallet, fundationid):
    blocked_id = 0

    #ajoute la personne a bloquer
    data = '{"usr_id":'+str(usr_id)+',"wallet":'+str(wallet)+',"raison":"fils de ta maman","fun_id":'+str(fundationid)+',"date_fin":"2018-03-05T22:59:00.000Z"}'
    response = requests.post('https://api.nemopay.net/services/BLOCKED/block', headers=headers, params=params, data=data)


    #reccupère le blo_id de la personne
    data='{"fun_id":2}'
    response = requests.post('https://api.nemopay.net/services/BLOCKED/getAll', headers=headers, params=params, data=data)
    json_data = json.loads(response.text)

    for key, value in json_data.items():
        if(value['wallet_id']==wallet):
            blocked_id = value['blo_id']
            print(value['login'],' ',value['blo_id'],'blocked')

    return blocked_id

#fonction débloquant un user à partir du blo_id et du fun_id
def unblock_User(fundationid, blo_id):
    data='{"fun_id":'+str(fundationid)+',"blo_id":'+str(blo_id)+'}'
    response = requests.post('https://api.nemopay.net/services/BLOCKED/remove', headers=headers, params=params, data=data)
    print("user unblocked")


def main():
    i=1
    block = 0
    while(i==1):
        if(block!=0):
            unblock_User(2,block)
            block = 0
        else:
            block = block_User(18506,8832,2)

        time.sleep(3)
    #print(block_User(15113, 5595, 2))
    #unblock_User(2,3998)
    #t = time.localtime()
    #2018-03-05T22:59:00.000Z

    #block_time = str(t.tm_year)+'-'+str(t.tm_mon%10)+'-'+str(t.tm_mday%10)+'T'+str(t.tm_hour)+':'+str(t.tm_min+10)+':'+str(t.tm_sec)+'.000Z'






main()

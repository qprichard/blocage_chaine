import requests


def changer(mot, sessionid):
    headers = {
        'Host': 'api.nemopay.net',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
        'Accept': 'application/json',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://admin.nemopay.net/',
        'Content-Type': 'application/json',
        'Content-Length': '78',
        'Origin': 'https://admin.nemopay.net',
        'Connection': 'keep-alive',
    }

    params = (
        ('system_id', 'payutc'),
        ('app_key', '0a93e8e18e6ed78fa50c4d74e949801b'),
        ('sessionid', str(sessionid)),
    )
    data = '{"fun_id":2,"message":"'+str(mot)+'"}'


    response = requests.post('https://api.nemopay.net/services/MESSAGE/changeMsg', headers=headers, params=params, data=data)

#NB. Original query string below. It seems impossible to parse and
#reproduce query strings 100% accurately so the one below is given
#in case the reproduced version is not "correct".
# response = requests.get('https://api.nemopay.net/services/MESSAGE/changeMsg?system_id=payutc&app_key=0a93e8e18e6ed78fa50c4d74e949801b&sessionid=jfi4oq85wxc7bg994tuvqmmmzijzayoc', headers=headers)

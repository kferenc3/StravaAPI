from datetime import timedelta
from datetime import datetime
from test import URL_BASE
from stravalib.client import Client
import os
import time as t
import requests
import traceback

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')
ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
EXPIRES_AT = os.environ.get('EXPIRES_AT')
URL_BASE = 'https://www.strava.com/api/v3/'
REDIRECT_URL = 'localhost'
ATHLETE_ID = '44086627'


def exp_checker(exp):
    tdlt = datetime.fromtimestamp(int(exp)) - datetime.today()

    if tdlt.seconds <= 600 or tdlt.days < 0:
        return('expired')
    else:
        return('ok')

def token_refresh():
    client = Client()
    resp = client.refresh_access_token(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,refresh_token=REFRESH_TOKEN)
    os.environ['ACCESS_TOKEN'] = resp['access_token']
    os.environ['EXPIRES_AT'] = str(resp['expires_at'])
    with open('dat', 'w') as dat:
        for key in resp:
            if key in ['access_token','expires_at']:
                dat.write(key+' '+str(resp[key])+'\n')
    dat.close
    os.system('token_replace.bat')
    

def get_activities():
    """The aim for this function is to check the last activity in the DBd and fetch any new after that.
    For now this will be a static 7 day fetch."""
    client = Client(access_token=ACCESS_TOKEN)
    aftr = datetime.today() - timedelta(days=7)
    acts = client.get_activities(after=aftr)
    actList = []
    for i in acts:
        actList.append(i.id)
    return actList

"""resp = requests.get('https://www.strava.com/api/v3/activities/5675641194',headers={'Authorization':'Bearer ' + ACCESS_TOKEN})"""

"""
client = Client()
print(datetime.datetime.fromtimestamp(resp['expires_at']).strftime('%c'))
"print(client.exchange_code_for_token(CLIENT_ID,CLIENT_SECRET,'f4c4298d384a98a1ea577b6f26d8b82f3ecfa497'))"

print (resp.json())

BASE/athlete
BASE/athlete/zones
BASE/activities/ID/streams?keys=heartrate
BASE/activities/ID/streams


http://www.strava.com/oauth/authorize?client_id=47499&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all

"""

if __name__ == '__main__':
    
    try:
        exp = exp_checker(EXPIRES_AT)
        if exp == 'ok':
            print('OK')
            print(get_activities())

        else:
            token_refresh()
            print(get_activities())
            
    except Exception:
        print(traceback.format_exception(BaseException,BaseException,None))
        print(datetime.now())


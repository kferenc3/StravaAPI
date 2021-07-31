from datetime import timedelta
from datetime import datetime
from stravalib.client import Client
import os
import time as t
import requests
import traceback

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')
"""ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')"""
EXPIRES_AT = os.environ.get('EXPIRES_AT')
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
    """SCRIPT HERE TO PERMANENTLY REPLACE THE VARIABLES"""
    

def get_activities():
    """The aim for this function is to check the last activity in the DBd and fetch any new after that.
    For now this will be a static 7 day fetch."""
    client = Client()
    aftr = datetime.datetime.today() - timedelta(days=7)
    acts = client.get_activities(after=aftr)
    actList = []
    for i in acts:
        actList.append(i.id)

"""resp = requests.get('https://www.strava.com/api/v3/activities/5675641194',headers={'Authorization':'Bearer ' + ACCESS_TOKEN})"""

"""
client = Client()
print(datetime.datetime.fromtimestamp(resp['expires_at']).strftime('%c'))
"print(client.exchange_code_for_token(CLIENT_ID,CLIENT_SECRET,'f4c4298d384a98a1ea577b6f26d8b82f3ecfa497'))"

print (resp.json())



http://www.strava.com/oauth/authorize?client_id=47499&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all

"""

if __name__ == '__main__':
    
    try:
        
        exp = exp_checker(EXPIRES_AT)
        if exp == 'ok':
            "CODE COMES HERE"
            print('OK')
        else:
            print('As the token will expire soon, it will be refreshed.')
            print('.')
            t.sleep(1)
            token_refresh()
            t.sleep(1)
            print('.')
            print('New token has been generated and credentials are refreshed.')
    
    except Exception:
        print(traceback.format_exception(BaseException,BaseException,None))
        print(datetime.now())


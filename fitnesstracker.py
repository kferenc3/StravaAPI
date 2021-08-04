from datetime import timedelta
from datetime import datetime
from stravalib.client import Client
import os
import time as t
import requests
import traceback
import polyline
import json
import pandas as pd

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
        print('The token expires in %s minutes' % str(round(tdlt.seconds/60,0)))
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
    

def get_activitylist():
    """The aim for this function is to check the last activity in the DBd and fetch any new after that.
    For now this will be a static 7 day fetch."""
    client = Client(access_token=ACCESS_TOKEN)
    aftr = datetime.today() - timedelta(days=7)
    acts = client.get_activities(after=aftr)
    actList = []
    for i in acts:
        actList.append(i.id)
    return actList

def latlng_encoder(resp):
    j = resp.json()
    for i in j:
        if i['type'] == 'latlng':
            p = polyline.encode(i['data'])
    return p

def get_segments(resp):
    dat = json.load(resp)
    headers = ['id', 'name', 'activity_type', 'distance', 'average_grade',
                'maximum_grade', 'elevation_high', 'elevation_low', 'start_latitude', 'start_longitude', 
                'end_latitude', 'end_longitude', 'climb_category', 'city', 'state', 'country',
                'private', 'hazardous', 'starred']
    renamedict = {'id':'segment_id','start_latitude': 'start_lat', 'start_longitude': 'start_lng',
        'end_latitude':'end_lat', 'end_longitude':'end_lng','city':'seg_city', 
        'state':'seg_state', 'country':'seg_country'}
    df = pd.DataFrame()
    keylist = []
    for efforts in dat['segment_efforts']:
        seg = efforts['segment']
        df = df.append(pd.DataFrame.from_dict(seg))
        for key in seg:
            keylist.append(key)
            
    keylist = list(set(keylist))
    l = [x for x in keylist if x not in headers]
    df = df.drop_duplicates().drop(columns=l).filter(like='0',axis=0)
    df = df.rename(columns=renamedict)
    return df


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
            "print(get_activities())"

        else:
            token_refresh()
            "print(get_activities())"
            
    except Exception:
        print(traceback.format_exception(BaseException,BaseException,None))
        print(datetime.now())


from datetime import timedelta
from datetime import datetime
from stravalib.client import Client
import os
import requests
import traceback
import polyline
import json
import pandas as pd
import csv

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')
EXPIRES_AT = os.environ.get('EXPIRES_AT')
URL_BASE = 'https://www.strava.com/api/v3/'


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
    var = resp['access_token']
    with open('dat', 'w') as dat:
        for key in resp:
            if key in ['access_token','expires_at']:
                dat.write(key+' '+str(resp[key])+'\n')
    dat.close
    os.system('token_replace.bat')
    return var
    

def get_activitylist():
    """The aim for this function is to check the last activity in the DB and fetch any new one after that.
    For now this will be a static 7 day fetch."""
    client = Client(access_token=ACCESS_TOKEN)
    aftr = datetime.today() - timedelta(days=7)
    acts = client.get_activities(after=aftr)
    actList = []
    for i in acts:
        actList.append(i.id)
    return actList

def get_activity(actid):
    "for i in lst:"
    resp = requests.get(URL_BASE + 'activities/'+ actid,headers={'Authorization':'Bearer ' + ACCESS_TOKEN}).text
    return resp

def latlng_encoder(resp):
    j = json.loads(resp)
    for i in j:
        if i['type'] == 'latlng':
            p = polyline.encode(i['data'])
    return p

def segments_efforts(resp,typ):
    
    dat = json.loads(resp)

    df = pd.DataFrame()
    if typ == 'activity':
        df = pd.DataFrame(pd.json_normalize(dat))
        df[['start_lat','start_lng']] = pd.DataFrame(df.start_latlng.tolist(), index=df.index)
        df[['end_lat','end_lng']] = pd.DataFrame(df.end_latlng.tolist(), index=df.index)
    elif typ == 'segment':
        for efforts in dat['segment_efforts']:
            seg = efforts['segment']
            df = df.append(pd.json_normalize(seg))
    elif typ == 'segment_efforts':
        for efforts in dat['segment_efforts']:
            df = df.append(pd.json_normalize(efforts))
    else:
        print('Invalid request type. The type: '+str(typ)+' is unknown.')

    return df

def df_reorg(datfr, hdr, rnm, typ):
    df_src = datfr
    head = pd.read_csv(hdr)
    head = head[typ].dropna()
    headers = head.tolist()
    with open (rnm, mode='r') as f:
        reader = csv.reader(f)
        row1 = next(reader)
        dictpos= [i for i,x in enumerate(row1) if x==typ]
        renamedict = dict((rows[dictpos[0]],rows[dictpos[1]]) for rows in reader)
    keylist = list(df_src.columns.values)
    l = [x for x in keylist if x not in headers]
    df = df_src.drop(columns=l).filter(like='0',axis=0).drop_duplicates()
    df = df.rename(columns=renamedict)

    return df

def segment_stream(id):
    url = URL_BASE + 'segments/'+str(id)+'/streams?keys=latlng'
    r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN}).text
    return r

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
        if exp != 'ok':
            ACCESS_TOKEN = token_refresh()
        else:
            ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
        typelist = ['activity','segment','segment_efforts']
        activities = get_activitylist()
        for act in activities:
            r = get_activity(str(act))
            df = pd.DataFrame()
            for i in range(len(typelist)):
                df = segments_efforts(r,typelist[i])
                df_clean = df_reorg(df,'headers.csv','dicts.csv',typelist[i])
                if typelist[i] == 'segment':
                    segments= df_clean['segment_id'].tolist()
                    for seg in segments:
                        latlng_encoder(segment_stream(seg))
                df_clean.to_csv(str(act)+'_'+str(typelist[i])+'.csv')
            
    except Exception:
        print(traceback.format_exception(BaseException,BaseException,None))
        print(datetime.now())


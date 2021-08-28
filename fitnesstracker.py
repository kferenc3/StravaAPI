from datetime import timedelta
from datetime import datetime
from stravalib import Client
import time as t
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

def ratelimit_checker(resp):
    limits = resp.headers['X-RateLimit-Usage'].split(',')
    if int(limits[0]) >= 95:
        t.sleep(60)
        print('Due to high usage suspending run for 1 minute')
    elif int(limits[1]) >= 990:
        print('Today\'s limit reached. No more requests')
        exit()
    else:
        return limits

def get_activitylist():
    """The aim for this function is to check the last activity in the DB and fetch any new one after that.
    For now this will be a static 7 day fetch."""
    
    aftr = (datetime.today() - timedelta(days=7)).timestamp()
    url = url_constructor('activity_list')+str(aftr)
    r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN})
    acts = json.loads(r.text)
    actList = []
    for i in acts:
        actList.append(i['id'])
    print(actList)    
    return actList

def url_constructor(type, id=None):
    if type == 'athlete':
        url = URL_BASE+'athlete'
    elif type == 'zones':
        url = URL_BASE+'athlete/zones'
    elif type == 'activity':
        url = URL_BASE+'activities/'+str(id)
    elif type == 'act_stream':
        url = URL_BASE+'activities/'+str(id)+'/streams?keys=heartrate'
    elif type == 'seg_stream':
        url = URL_BASE+'segments/'+str(id)+'/streams?keys=latlng'
    elif type == 'activity_list':
        url=URL_BASE+'/athlete/activities?after='
    
    return url

def get_response(type, id=None):
    url = url_constructor(type, id)
    resp = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN})
    return resp

def latlng_encoder(resp):
    resp = resp.text
    j = json.loads(resp)
    for i in j:
        if i['type'] == 'latlng':
            p = polyline.encode(i['data'])
    return p

def df_from_response(resp,typ):
    resp = resp.text
    dat = json.loads(resp)
    if 'message' in dat:
        t.sleep(60)

    df = pd.DataFrame()
    if typ == 'activity':
        df = pd.DataFrame(pd.json_normalize(dat))
        if (df['start_latlng'].str.len()!=0).values:
            df[['start_lat','start_lng']] = pd.DataFrame(df.start_latlng.tolist(), index=df.index)
            df[['end_lat','end_lng']] = pd.DataFrame(df.end_latlng.tolist(), index=df.index)
        else:
            df[['start_lat','start_lng']] = pd.DataFrame([['NULL','NULL']],index=df.index)
            df[['end_lat','end_lng']] = pd.DataFrame([['NULL','NULL']],index=df.index)
    
    elif typ in ['activity_metrics','gear','map','athlete']:
        df = pd.DataFrame(pd.json_normalize(dat))
    
    elif typ == 'segment':
        for efforts in dat['segment_efforts']:
            seg = efforts['segment']
            df = df.append(pd.json_normalize(seg))
    
    elif typ == 'segment_efforts':
        for efforts in dat['segment_efforts']:
            df = df.append(pd.json_normalize(efforts))
    
    elif typ == 'splits':
        if 'splits_metric' in dat:
            split_type = []
            actid = dat['id']
            for splits in dat['splits_metric']:
                df = df.append(pd.json_normalize(splits))
                split_type.append('splits_metrics')
            for splits in dat['splits_standard']:
                df = df.append(pd.json_normalize(splits))
                split_type.append('splits_standard')
            df['split_type'] = split_type
            df['activity_id'] = actid
    
    elif typ == 'laps':
        for lap in dat['laps']:
            df = df.append(pd.json_normalize(lap))

    elif typ == 'best_efforts':
        if 'best_efforts' in dat:
            for bf in dat['best_efforts']:
                df = df.append(pd.json_normalize(bf))
    
    elif typ == 'clubs':
        for club in dat['clubs']:
            df = df.append(pd.json_normalize(club))
    
    elif typ == 'zones':
        df = pd.json_normalize(dat['heart_rate']['zones'])
    
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
        ath = get_response('athlete')
        print(ratelimit_checker(ath))        
        athletetype = ['athlete','clubs']
        for at in athletetype:
            df_ath = df_from_response(ath,at)
            if at == 'athlete':
                athid = df_ath['id'].values
            df_ath = df_reorg(df_ath,'headers.csv','dicts.csv',at)
        activitytype = ['activity','activity_metrics','segment','segment_efforts','gear','map','splits','laps','best_efforts']
        activities = get_activitylist()
        for act in activities:
            r = get_response('activity',act)
            df = pd.DataFrame()
            for typ in activitytype:
                df = df_from_response(r,typ)
                df_clean = df_reorg(df,'headers.csv','dicts.csv',typ)
                if typ == 'segment' and 'segment_id' in df_clean:
                    segments= df_clean['segment_id'].tolist()
                    for seg in segments:
                        latlng_encoder(get_response('seg_stream',seg))     
                df_clean.to_csv(typ+'-'+str(act)+'.csv')  
        z = get_response('zones')
        zone_df = df_from_response(z,'zones')
        zone_df['athlete_id'] = str(athid[0])
        zone_df['zone_type'] ='heart_rate'
        print(ratelimit_checker(r))
            
    except Exception:
        traceback.print_exception()
        print(datetime.now())


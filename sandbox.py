from datetime import timedelta
from datetime import datetime
import numpy
from stravalib import Client
import time as t
import os
import requests
import traceback
import polyline
import json
import pandas as pd
import csv
import DBfunctions

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
    aftr = DBfunctions.extract_date()
    url = url_constructor('activity_list')+str(aftr)+'&per_page=10'
    r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN})
    acts = json.loads(r.text)
    actList = []
    for i in acts:
        actList.append(i['id'])   
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
    df = pd.DataFrame()
    if typ == 'activity':
        df = pd.DataFrame(pd.json_normalize(dat))
        if (df['start_latlng'].str.len()!=0).values:
            df[['start_lat','start_lng']] = pd.DataFrame(df.start_latlng.tolist(), index=df.index)
            df[['end_lat','end_lng']] = pd.DataFrame(df.end_latlng.tolist(), index=df.index)
        else:
            df[['start_lat','start_lng']] = pd.DataFrame([[None,None]],index=df.index)
            df[['end_lat','end_lng']] = pd.DataFrame([[None,None]],index=df.index)
    
    elif typ in ['activity_metrics','gear','maps','athlete']:
        df = pd.DataFrame(pd.json_normalize(dat))
    
    elif typ == 'segments':
        for efforts in dat['segment_efforts']:
            seg = efforts['segment']
            df = df.append(pd.json_normalize(seg))
    
    elif typ == 'segment_effort':
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
        if 'laps' in dat:
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
    for r in ['city','state','country']:
        df_filt = df.filter(regex=r+'$').drop_duplicates().dropna(axis=0)
        engine, metadata = DBfunctions.db_connect()
        if not df_filt.empty:
            filt_lst = df_filt[df_filt.columns[0]].tolist()
            if '' in filt_lst:
                filt_lst.remove('')
            if 'Magyarország' in filt_lst:
                filt_lst.remove('Magyarország')
            cnt, lst = DBfunctions.check_record(r,r+'_name',filt_lst,engine,metadata)
            filt_lst = [x for x in filt_lst if x not in lst]
            if len(filt_lst) >0:
                for it in filt_lst:
                    DBfunctions.insert_record(r,it,engine,metadata)
    cities = DBfunctions.location_dict('city')
    states = DBfunctions.location_dict('state')
    countries = DBfunctions.location_dict('country')
    df.replace(r"^\s*$",numpy.NaN,regex=True,inplace=True)
    df.replace({"Magyarország": "Hungary"},inplace=True)
    df.replace(cities,inplace=True)
    df.replace(states,inplace=True)
    df.replace(countries,inplace=True)
    if 'actsegment_id' in df:
        df['map_type'] = 'activity'
    
    return df

def segment_stream(id):
    url = URL_BASE + 'segments/'+str(id)+'/streams?keys=latlng'
    r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN}).text
    return r

def hear_rate_stream(id):
    url = URL_BASE + 'activities/'+str(id)+'/streams?keys=heartrate'
    r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN}).text
    actid=[]
    dist=[]
    hr=[]
    j = json.loads(r)
    if 'message' in j:
        print('No HR data')
        df = pd.DataFrame()
    else:
        for i in j:
            if i['type']=='distance':
                actid = [id for x in i['data']]
                dist=[x for x in i['data']]
            elif i['type']=='heartrate':
                hr=[x for x in i['data']]
        df = pd.DataFrame({'activity_id': actid,'dist':dist,'heart_rate':hr})
    return df
    
def df_init(r,t):
    df = pd.DataFrame()
    df = df_from_response(r,t)
    df_clean = df_reorg(df,'headers.csv','dicts.csv',t)
    return df_clean


if __name__ == '__main__':
    
    try:
        exp = exp_checker(EXPIRES_AT)
        if exp != 'ok':
            ACCESS_TOKEN = token_refresh()
        else:
            ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
        engine, metadata = DBfunctions.db_connect()
        ath = get_response('athlete')
        print(ratelimit_checker(ath))        
        athletetype = ['athlete','clubs']
        for at in athletetype:
            df_ath = df_init(ath,at)
        activitytype = ['activity','activity_metrics','segments','segment_effort','gear','maps','splits','laps','best_efforts']
        activities = get_activitylist()
        cnt, lst = DBfunctions.check_record('activity','activity_id',activities,engine,metadata)
        activities = [x for x in activities if x not in lst]
        for act in activities:
            r = get_response('activity',act)
            for typ in activitytype:
                df_clean = df_init(r,typ)
            df_hr = hear_rate_stream(act)

    except Exception:
        traceback.print_exception()
        print(datetime.now())

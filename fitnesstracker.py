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
        token = token_refresh()
    else:
        print('The token expires in %s minutes' % str(round(tdlt.seconds/60,0)))
        token = os.environ.get('ACCESS_TOKEN')
    return token

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
        wait_time = (15 - int(t.strftime('%M',(t.localtime())))%15)*60
        print('Due to high usage restart needed in %s minutes' % str(round(wait_time/60,1)))
        t.sleep(wait_time)
        print('The wait is over')
    elif int(limits[1]) >= 990:
        print('Today\'s limit reached. No more requests')
        exit()
    else:
        return limits

def get_activitylist(eng,met):
    aftr = DBfunctions.extract_date()
    url = url_constructor('activity_list')+str(aftr)+'&per_page=10'
    r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN})
    acts = json.loads(r.text)
    actList = []
    for i in acts:
        actList.append(i['id'])
    cnt, lst = DBfunctions.check_record('activity','activity_id',actList,eng,met)
    actList = [x for x in actList if x not in lst]   
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
    ratelimit_checker(resp)
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
    df_filt = df.filter(regex='device_id').drop_duplicates().dropna(axis=0)
    engine, metadata = DBfunctions.db_connect()
    if not df_filt.empty:
        filt_lst = df_filt[df_filt.columns[0]].tolist()
        if '' in filt_lst:
            filt_lst.remove('')
        cnt, lst = DBfunctions.check_record('device','device_name',filt_lst,engine,metadata)
        filt_lst = [x for x in filt_lst if x not in lst]
        if len(filt_lst) >0:
            for it in filt_lst:
                DBfunctions.insert_record('device',it,engine,metadata)
    rplc = ['city','state','country','device']
    df.replace(r"^\s*$",numpy.NaN,regex=True,inplace=True)
    df.replace({"Magyarország": "Hungary"},inplace=True)
    for i in rplc:
        rep_dict = DBfunctions.location_dict(i)
        df.replace(rep_dict,inplace=True) 
    if 'actsegment_id' in df:
        df['map_type'] = 'activity'
    
    return df

def segment_stream(id):
    url = URL_BASE + 'segments/'+str(id)+'/streams?keys=latlng'
    r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN}).text
    return r

def hear_rate_stream(id, eng):
    url = URL_BASE + 'activities/'+str(id)+'/streams?keys=heartrate'
    r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN}).text
    actid=[]
    dist=[]
    hr=[]
    j = json.loads(r)
    if 'message' in j:
        status = 'No HR data'
        df = pd.DataFrame()
    else:
        for i in j:
            if i['type']=='distance' or i['type']=='time':
                actid = [id for x in i['data']]
                dist=[x for x in i['data']]
                metrtyp=[i['type'] for x in i['data']]
            elif i['type']=='heartrate':
                hr=[x for x in i['data']]
        if len(actid)==len(dist)==len(hr):
            df = pd.DataFrame({'activity_id': actid,'metric':dist,'heart_rate':hr,'metric_type':metrtyp})
        else:
            df = pd.DataFrame()
    if not df.empty:    
        df.to_sql('heart_rate',con=eng,schema='dwh',if_exists='append',index=False)
        status = 'HR load successful.'
    return status

def zone_update(ath,eng):
    z = get_response('zones')
    zone_df = df_from_response(z,'zones')
    zone_df['athlete_id'] = str(ath)
    zone_df['zone_type'] ='heart_rate'
    zone_df['zone_num'] = [1,2,3,4,5]
    with engine.connect() as conn:
        df_curr = pd.read_sql_table('zones',conn,'dwh')
        conn.close()
    if zone_df.equals(df_curr):
        status = 'No zone update needed.'
    else:
        zone_df.to_sql('zones',con=eng,schema='dwh',if_exists='replace',index=False)
        status = 'Zones have been loaded!'
    return status

    
def df_init(r,t):
    df = pd.DataFrame()
    df = df_from_response(r,t)
    df_clean = df_reorg(df,'headers.csv','dicts.csv',t)
    return df_clean

def athlete_club_load(eng, met):
    ath = get_response('athlete')       
    athletetype = ['athlete','clubs']
    for at in athletetype:
        df_ath = df_init(ath,at)
        if at == 'athlete':
            athid = df_ath['athlete_id'].values.tolist()
            cnt, lst = DBfunctions.check_record(at,'athlete_id',athid,eng,met)
            if cnt!=len(athid):
                df_ath = df_ath.loc[~df_ath['athlete_id'].isin(lst)]
                df_ath.to_sql(at,con=eng,schema='dwh', if_exists='append',index=False)
            else:
                print('No new athlete to load!')
        elif at == 'clubs':
            clubid = df_ath['club_id'].values.tolist()
            cnt, lst = DBfunctions.check_record(at,'club_id',clubid,eng,met)
            if cnt!=len(clubid):
                df_ath = df_ath.loc[~df_ath['club_id'].isin(lst)]
                df_ath.to_sql(at,con=eng,schema='dwh', if_exists='append',index=False)
            else:
                print('No new clubs to load!')
    return athid

def activity_load(activities,activitytype,engine,metadata):
    for act in activities:
                r = get_response('activity',act)
                for typ in activitytype:
                    df_clean = df_init(r,typ)
                    if typ == 'segments' and 'segment_id' in df_clean:
                        segments = df_clean['segment_id'].tolist()
                        cnt, lst = DBfunctions.check_record('segments','segment_id',segments,engine,metadata)
                        segments = [x for x in segments if x not in lst]
                        df_clean = df_clean.loc[df_clean['segment_id'].isin(segments)]
                        df_clean.to_sql(typ,con=engine,schema='dwh',if_exists='append',index=False)
                        print(str(typ)+' has been loaded!')
                        for seg in segments:
                            p = latlng_encoder(get_response('seg_stream',seg))
                            df_map = pd.DataFrame({'actsegment_id': seg,'map_type':'segment','polyline': p},index=[0])
                            df_map.to_sql('maps',con=engine,schema='dwh',if_exists='append',index=False)
                            print('Segment '+str(seg)+' map has been loaded!')
                    elif typ == 'gear':
                        if 'gear_id' in df_clean:
                            df_clean['gear_type'] = 'shoes'
                            cnt, lst = DBfunctions.check_record('gear', 'gear_id',df_clean['gear_id'].tolist(),engine,metadata)
                            if df_clean['gear_id'].values in lst:
                                DBfunctions.update_record('gear',df_clean.to_dict('records'),'gear_id',engine,metadata)
                            else:
                                df_clean.to_sql(typ,con=engine,schema='dwh',if_exists='append',index=False)
                                print(str(typ)+' has been loaded!')
                    elif typ == 'maps':
                        df_test = df_clean.isna()
                        if df_test['polyline'].values!=True:
                            df_clean.to_sql(typ,con=engine,schema='dwh',if_exists='append',index=False)
                            print('Activity map'+'-'+str(act)+' have been loaded!')
                    else:
                        df_clean.to_sql(typ,con=engine,schema='dwh',if_exists='append',index=False)
                        print(str(typ)+' has been loaded!')
                print(hear_rate_stream(act,engine))

if __name__ == '__main__':
    
    try:
        ACCESS_TOKEN=exp_checker(EXPIRES_AT)
        engine, metadata = DBfunctions.db_connect()
        athid = athlete_club_load(engine, metadata)
        activitytype = ['activity','activity_metrics','segments','segment_effort','gear','maps','splits','laps','best_efforts']
        activities = get_activitylist(engine,metadata)
        activity_load(activities,activitytype,engine,metadata)
        print(zone_update(athid[0],engine))
            
    except Exception:
        traceback.print_exception()
        print(datetime.now())


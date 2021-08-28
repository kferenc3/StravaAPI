from datetime import datetime
from datetime import timedelta
import os
import pandas as pd
from pandas.core.frame import DataFrame
from polyline import encode
import requests
import json
import time as t
import csv


ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
URL_BASE = 'https://www.strava.com/api/v3/'


"url = URL_BASE+'athlete'"
aftr = (datetime.today() - timedelta(days=7)).timestamp()
url=URL_BASE+'/activities/5800395913'

'gps:5790079526'
'treadmill:5800282979'
'wheigth training: 5800395913'


"""limits = r.headers['X-RateLimit-Usage'].split(',')
if int(limits[0]) >= 95:
    t.sleep(60)
    print('Due to high rate limit suspending run for 1 minute')
elif int(limits[1]) >= 990:
    print('Today\'s limit reached. No more requests')
    exit()
else:
    print('Only %s requests are used. Good to go!' % str(limits[0]))
    print('Daily usage (out of a 1000): %s' % str(limits[1]))"""


activitytype = ['activity','activity_metrics','segment','segment_efforts','gear','map','splits','laps','best_efforts']

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
        print('Activity!')
    
    elif typ in ['activity_metrics','gear','map','athlete']:
        df = pd.DataFrame(pd.json_normalize(dat))
        if typ=='activity_metrics':
            print('activity_metrics')
        elif typ=='gear':
            print('gear')
        elif typ=='map':
            print('map')
        else:
            print('athlete')
    
    elif typ == 'segment':
        for efforts in dat['segment_efforts']:
            seg = efforts['segment']
            df = df.append(pd.json_normalize(seg))
        print('segment')
    
    elif typ == 'segment_efforts':
        for efforts in dat['segment_efforts']:
            df = df.append(pd.json_normalize(efforts))
        print('segment_efforts')
    
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





if __name__ == '__main__':
    r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN})
    acts = json.loads(r.text)
    df = pd.DataFrame(pd.json_normalize(acts))
    for typ in activitytype:
        df = df_from_response(r,typ)
        df_clean = df_reorg(df,'headers.csv','dicts.csv',typ)
        if typ == 'segment' and 'segment_id' in df_clean:
            segments= df_clean['segment_id'].tolist()
            """for seg in segments:
                latlng_encoder(get_response('seg_stream',seg)) """   




"""url = URL_BASE + 'segments/'+str(id)+'/streams?keys=latlng'
url = URL_BASE + 'athlete'
url = URL_BASE + 'athlete/zones'
url = URL_BASE + 'activities/'+str(actid)
url = URL_BASE + 'activities/'+str(actid)+'/streams?keys=heartrate'"""

def url_constructor(type, id):
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

"""
streams?keys=latlng'
BASE/athlete
BASE/athlete/zones
BASE/activities/ID/streams?keys=heartrate
BASE/activities/ID/streams
BASE/segments/id/streams?keys=latlng

"""
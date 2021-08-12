from datetime import datetime
import os
import json
import pandas as pd
from pandas.core.frame import DataFrame
from polyline import encode
import re
import requests
import csv


ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
URL_BASE = 'https://www.strava.com/api/v3/'


"url = URL_BASE+'athlete'"
url=URL_BASE+'/athlete'
resp = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN}).text

dat = json.loads(resp)
df = pd.DataFrame()
df = df.append(pd.json_normalize(dat))

df.to_csv('best_efforts.csv')


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
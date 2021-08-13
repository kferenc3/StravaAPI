from datetime import datetime
from datetime import timedelta
import os
import pandas as pd
from pandas.core.frame import DataFrame
from polyline import encode
import requests
import json
import time as t


ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
URL_BASE = 'https://www.strava.com/api/v3/'


"url = URL_BASE+'athlete'"
aftr = (datetime.today() - timedelta(days=7)).timestamp()
url=URL_BASE+'/athlete/activities?after='+str(aftr)

r = requests.get(url,headers={'Authorization':'Bearer ' + ACCESS_TOKEN})
limits = r.headers['X-RateLimit-Usage'].split(',')
if int(limits[0]) >= 95:
    t.sleep(60)
    print('Due to high rate limit suspending run for 1 minute')
elif int(limits[1]) >= 990:
    print('Today\'s limit reached. No more requests')
    exit()
else:
    print('Only %s requests are used. Good to go!' % str(limits[0]))
    print('Daily usage (out of a 1000): %s' % str(limits[1]))

acts = json.loads(r.text)
actList = []
for i in acts:
    actList.append(i['id'])


print(actList)




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
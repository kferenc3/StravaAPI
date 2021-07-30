import datetime
from datetime import timedelta
from datetime import datetime
from stravalib.client import Client
import os
import requests

CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REFRESH_TOKEN = os.environ.get('REFRESH_TOKEN')
EXPIRES_AT = os.environ.get('EXPIRES_AT')
REDIRECT_URL = 'localhost'
ATHLETE_ID = '44086627'


def exp_checker(exp):
    exp_date = datetime.fromtimestamp(int(exp))
    tdlt = exp_date - datetime.today()
    if tdlt.seconds < 0:
        return('expired')
    elif tdlt.seconds > 0 and tdlt.seconds <= 600:
        return('10min')
    else:
        return('ok')

if __name__ == '__main__':
    print(exp_checker(EXPIRES_AT))




"""
client = Client()
resp = client.refresh_access_token(client_id=CLIENT_ID,client_secret=CLIENT_SECRET,refresh_token=REFRESH_TOKEN)
if str(resp['expires_at']) == os.environ.get('EXPIRES_AT'):
    print('fuckyeh!')
    ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
    EXPIRES_AT = os.environ.get('EXPIRES_AT')
else:
    print('oh no!')
    os.environ['ACCESS_TOKEN'] = resp['access_token']
    os.environ['EXPIRES_AT'] = str(resp['expires_at'])

ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
EXPIRES_AT = os.environ.get('EXPIRES_AT')

print(datetime.datetime.fromtimestamp(resp['expires_at']).strftime('%c'))
"print(client.exchange_code_for_token(CLIENT_ID,CLIENT_SECRET,'f4c4298d384a98a1ea577b6f26d8b82f3ecfa497'))"
resp = requests.get('https://www.strava.com/api/v3/activities/5675641194',headers={'Authorization':'Bearer'})
print (resp.json())


{'access_token': 'f75fd3925535aa000e215b11e7b7cfb7de802cc9', 
'refresh_token': '27788e030a96165708086f907250d3a77daecf28', 
'expires_at': 1627598983}
http://www.strava.com/oauth/authorize?client_id=47499&response_type=code&redirect_uri=http://localhost/exchange_token&approval_prompt=force&scope=profile:read_all,activity:read_all





aftr = datetime.datetime.today() - timedelta(days=7)
acts = client.get_activities(after=aftr)
actList = []
for i in acts:
    actList.append(i.id)

testact = client.get_activity(actList[0]).to_dict

print(testact)
"""
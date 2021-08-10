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
"""
resp = requests.get('https://www.strava.com/api/v3/activities/5675641194',headers={'Authorization':'Bearer ' + ACCESS_TOKEN}).text

source = json.loads(resp)

with open('testresp.json','w') as f:
    json.dump(source,f)
    

dat = json.load(f)

headers = ['id', 'name', 'activity_type', 'distance', 'average_grade',
            'maximum_grade', 'elevation_high', 'elevation_low', 'start_latitude', 'start_longitude', 
            'end_latitude', 'end_longitude', 'climb_category', 'city', 'state', 'country',
            'private', 'hazardous', 'starred']
renamedict = {'id':'segment_id','start_latitude': 'start_lat', 'start_longitude': 'start_lng',
    'end_latitude':'end_lat', 'end_longitude':'end_lng','city':'seg_city', 'state':'seg_state', 'country':'seg_country'}

for i in range(len(headers)):
    print(list(headers[i]))
    data = headers[i]=[]
print(data)
df = pd.DataFrame()
keylist = []
for efforts in dat['segment_efforts']:
    df = df.append(pd.json_normalize(efforts))
    for key in efforts:
        print(key, efforts[key])
    seg = efforts['segment']
    df = df.append(pd.DataFrame.from_dict(efforts))
    for key in seg:
        keylist.append(key)
        
keylist = list(set(keylist))
l = [x for x in keylist if x not in headers]
df = df.drop_duplicates().drop(columns=l).filter(like='0',axis=0)
df = df.rename(columns=renamedict)


df.rename(columns={'segment.id': 'seg_id'},inplace=True)
df = df.drop(list(df.filter(regex='segment*')),axis=1)


df.to_csv('test.csv')

def get_segments(resp):
    dat = json.loads(resp)
    headers = ['id', 'name', 'activity_type', 'distance', 'average_grade',
                'maximum_grade', 'elevation_high', 'elevation_low', 'start_latitude', 'start_longitude', 
                'end_latitude', 'end_longitude', 'climb_category', 'city', 'state', 'country',
                'private', 'hazardous', 'starred']
    renamedict = {'id':'segment_id','start_latitude': 'start_lat', 'start_longitude': 'start_lng',
        'end_latitude':'end_lat', 'end_longitude':'end_lng','city':'seg_city', 
        'state':'seg_state', 'country':'seg_country'}
    df = pd.DataFrame()
    for efforts in dat['segment_efforts']:
        seg = efforts['segment']
        df = df.append(pd.json_normalize(seg))
            
    keylist = list(df.columns.values)
    l = [x for x in keylist if x not in headers]
    df = df.drop(columns=l).filter(like='0',axis=0).drop_duplicates()
    df = df.rename(columns=renamedict)
    return df

def get_segmentefforts(resp):
    dat = json.loads(resp)
    headers = ['id','seg_id','activity.id','athlete.id','elapsed_time','moving_time',
    'start_date','start_date_local','distance','start_index','end_index','average_cadence',
    'average_heartrate','max_heartrate','pr_rank','kom_rank','hidden']
    renamedict = {'id':'segment_effort_id','seg_id':'segment_id','activity.id':'activity_id','athlete.id':'athlete_id',
    'average_heartrate':'average_hr','max_heartrate':'max_hr'}
    df = pd.DataFrame()
    for efforts in dat['segment_efforts']:
        df = df.append(pd.json_normalize(efforts))

    df.rename(columns={'segment.id': 'seg_id'},inplace=True)
    df = df.drop(list(df.filter(regex='segment*')),axis=1)
    keylist = list(df.columns.values)
    l = [x for x in keylist if x not in headers]
    df = df.drop(columns=l).filter(like='0',axis=0)
    df = df.rename(columns=renamedict)
    return df



"""

""

"""df = pd.DataFrame(data,columns=headers)
"""




"""f = open('testresponse.json',encoding='utf8')
p = re.compile('(?<!\\\\)\'')
str = p.sub('\"', f)
data = json.load(str)"""


"""
streams?keys=latlng'
BASE/athlete
BASE/athlete/zones
BASE/activities/ID/streams?keys=heartrate
BASE/activities/ID/streams
BASE/segments/id/streams?keys=latlng

for i in resp:
    if i['type'] == 'latlng':
        print('This!')
        p = polyline.encode(i['data'])
        print(p)
    else:
        print('NotThis!')
s = 'k~}`HklmsB?E?KIKIMGKEIGQKWIOMYACWa@GQAIWm@CGEWGKYa@KUSc@CESc@AEMo@Qk@CESQGU@C@G?AIOWg@Ou@Dg@G[Om@Qq@Ug@W]KQIQIWCGSm@O_@@EDCHJTJh@Bb@D\Jf@FB?`@AVG`@[XQXSNS^Mf@C\CXMB?VSHSBMDu@@EDm@Bq@Am@?EEg@Oi@Ym@CC_@[ACSUECGGIKCCY_@Y_@_@]e@QCGKKEGCCQSSW[_@_@c@W[WYa@YU_@SW]e@Wk@Wk@IQ?YOk@Oc@K[KQO][i@S_@EGIISWWW_@]UWEEQKECWI_@G]AMJEDEFWVEFKREPGRSh@IVELITIPS^EHGHc@\ON_@V_@XEFCP?XGp@Lj@T^LLXTb@VJF^XNNRPNHNTVf@Td@JPTf@DJDR@FJp@DRDT?DDNDNDNBLFJHPDDBBFJ?@BRJV?D@PLZ?BJ\@@HXLZR\Tb@L\@@FDNDP@JARGPIFCNENCF?P?D@H?H?L?LFPFXd@Tv@DHFFd@^`@TLDF@F?D?F?h@CJIDGDEDEDIBILg@`@Sb@Kf@EF?BAPI`@QFGXm@@KBw@@GDc@@q@?WCWES?AAO?CAIEKCGAOCECIAGIQCMKKGISWQSECWa@YUYOGEWOQOQSEGQUMMIIOQYYEEU[II_@g@CE[[MKEEEGIQSu@Wm@]k@Um@]m@Ye@[e@[m@O]MQ]c@KQOMWSOKSKOKEAKCMAGACAEAIAI@M@KBA@KBA?CBMLGFSXCDMXABQ^IXCNQb@OVCDIJOTKLSRSNIDMJKJWZQ\CH?HFv@Pl@LP`@ZD@f@Xb@\LJb@^DD\`@PTXd@HNXl@Nb@Hh@Jt@@H@HRn@FPRj@BFHb@CXH`@FLDFFFHFBBBF@JBH@F?@HRDL?DLT@@LZNNBHBBLF@AR@b@OBAFOBGT?H?FAD?V?N?NFNFDBLLHNBHDPVf@FFRPLF`@VDBLD^F^C^SVs@\a@DCf@EDAVA\E^QFC^g@BI?s@DWHi@@e@?SIg@CM?I?IAWIYCSCOEEGKKQ?AGKGG?AEEIKKMOQSOCCQYSQUKUKAAUWCCUWSWSWMOMMEGMKKMOUQUIKOSYa@Um@Um@CIEOUk@Yi@KQWm@[i@Wg@]c@IMa@i@QWSQ_@]MGe@SKEWEIAUEMAI?SDGBKFIDA@IFEFABEHGLGLEPKRCLA@CFCLIRAFMVCDABS`@CBMPQVQNEBOFMJEBKHGFCFMTMZEX?H@J@PJ`@Xf@DBb@V`@VNJHB`@XDBJJ^`@FLXd@JPT^NXTt@Nx@Np@JZ@JRp@FRRn@L`@Nx@BDHVB\@LBBXZJLD@@?HNDPHHHBB@B?LGPEL?FCTITCDAL@VHT@DAD@NFFBNRLZFPHRJLJLXPLHRHTBb@DLCVMDE^_@\_@`@QFAFCd@Gb@O^QDCTa@Fm@Hw@?K@w@@QGo@?GMi@Kq@QYEGISEEAEKKIIEGGEIGIIKIGIAEKOMIIGIC[SAAKIECU[]a@QWEGCGGKOOSUQSSWIISOOSEE[k@CIOi@IQWg@GKWo@CGYi@MQWi@EGYk@CGSYMQWa@EEYYc@[c@SEAg@Mg@GQBe@NKFIFGBQTCFGRGNCJEHGNEFCJCJELABGNEHADEFILW^a@\a@\ORGJQZIn@D\J`@Rb@BB^TRP^X^RNHNLVXPTTXHLVXBFR`@Pd@D^Fj@Lp@@HJd@BLP`@Tl@Tr@FVPl@Rl@Rf@\f@Zb@?@R@b@SXSb@IBA^@d@DDFNVHHN`@?f@Nd@Pb@Nl@Rh@Rn@P^BDHXFHRr@@BPf@Vh@Lp@J^Ph@DR?PNp@FFDJ@N@HHRN`@JZHVF\?DBDJXF^DJT^HV@DJV@BRf@Rb@Xd@FR@DRn@@DJ^@DBBBNL^@B@FBDBJFPHN'
l = polyline.decode(s)
print(l)

No latlng response: {'message': 'Resource Not Found', 'errors': []}
"""

f = open('testresp.json')



def segments_efforts(resp,typ,hdr,rnm):
    dat = json.load(resp)
    head = pd.read_csv(hdr)
    head = pd.DataFrame(head).dropna()
    headers = head[typ].tolist()
    with open (rnm, mode='r') as f:
        reader = csv.reader(f)
        row1 = next(reader)
        dictpos= [i for i,x in enumerate(row1) if x==typ]
        renamedict = dict((rows[dictpos[0]],rows[dictpos[1]]) for rows in reader)
    
    
    "renamedict = dcts[typ].to_dict()"
    "print(renamedict)"
    "['id', 'name', 'activity_type', 'distance', 'average_grade', 'maximum_grade', 'elevation_high', 'elevation_low', 'start_latitude', 'start_longitude', 'end_latitude', 'end_longitude', 'climb_category', 'city', 'state', 'country', 'private', 'hazardous', 'starred']"
    
    "{'id':'segment_id','start_latitude': 'start_lat', 'start_longitude': 'start_lng','end_latitude':'end_lat', 'end_longitude':'end_lng','city':'seg_city','state':'seg_state', 'country':'seg_country'}"
    df = pd.DataFrame()
    if typ == 'segment':
        for efforts in dat['segment_efforts']:
            seg = efforts['segment']
            df = df.append(pd.json_normalize(seg))
    elif typ == 'segment_efforts':
        for efforts in dat['segment_efforts']:
            df = df.append(pd.json_normalize(efforts))
    else:
        print('Invalid request type. The type: '+str(typ)+' is unknown.')
      
    keylist = list(df.columns.values)
    l = [x for x in keylist if x not in headers]

    df = df.drop(columns=l).filter(like='0',axis=0).drop_duplicates()
    df = df.rename(columns=renamedict)
    df.to_csv('test.csv')
    return df

def get_segmentefforts(resp):
    dat = json.loads(resp)
    headers = ['id','seg_id','activity.id','athlete.id','elapsed_time','moving_time', 'start_date','start_date_local','distance','start_index','end_index','average_cadence', 'average_heartrate','max_heartrate','pr_rank','kom_rank','hidden']
    renamedict = {'id':'segment_effort_id','seg_id':'segment_id','activity.id':'activity_id','athlete.id':'athlete_id',
    'average_heartrate':'average_hr','max_heartrate':'max_hr'}
    df = pd.DataFrame()
    for efforts in dat['segment_efforts']:
        df = df.append(pd.json_normalize(efforts))

    df.rename(columns={'segment.id': 'seg_id'},inplace=True)
    df = df.drop(list(df.filter(regex='segment*')),axis=1)
    keylist = list(df.columns.values)
    l = [x for x in keylist if x not in headers]
    df = df.drop(columns=l).filter(like='0',axis=0)
    df = df.rename(columns=renamedict)
    return df

segments_efforts(f,'segment_efforts','headers.csv','dicts.csv')

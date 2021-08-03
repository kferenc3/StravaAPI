import os
import json
import pandas as pd
from polyline import encode
import re
import requests


ACCESS_TOKEN = os.environ.get('ACCESS_TOKEN')
URL_BASE = 'https://www.strava.com/api/v3/'
"""
resp = requests.get('https://www.strava.com/api/v3/activities/5675641194',headers={'Authorization':'Bearer ' + ACCESS_TOKEN}).text

source = json.loads(resp)

with open('testresp.json','w') as f:
    json.dump(source,f)
    """
f = open('testresp.json')
dat = json.load(f)

headers = ['segment_id', 'name', 'activity_type']
""", 'distance', 'average_grade',
            'maximum_grade', 'elevation_high', 'elevation_low', 'start_lat', 'start_lng', 
            'end_lat', 'end_lng', 'climb_category', 'seg_city', 'seg_state', 'seg_country'
            'private', 'hazardous', 'starred'
               ]"""

data=[]
for efforts in dat['segment_efforts']:
    seg = json.loads(json.dumps(efforts['segment']))
    segment_id = seg['id']
    name = seg['name']
    activity_type = seg['activity_type']
    data.append([segment_id, name, activity_type])

print(data)

df = pd.DataFrame(data,columns=headers)
df = df.drop_duplicates()
print(df)


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



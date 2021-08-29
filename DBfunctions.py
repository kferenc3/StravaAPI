import sqlalchemy
import rsa
import os
import base64
import traceback


def pwd_en_de_crypt(msg, mode):
    privloc = os.environ.get('privfileloc')
    publoc = os.environ.get('pubfileloc')
    if mode == 'encrypt':
        with open(publoc,mode='rb') as pubfile:
            pubdat = pubfile.read()
            pubkey = rsa.PublicKey.load_pkcs1(pubdat)
        pwd_raw = msg.encode('utf8')
        pwd = rsa.encrypt(pwd_raw,pubkey)
    elif mode == 'decrypt':
        with open(privloc,mode='rb') as privfile:
            privdat = privfile.read()
            privkey = rsa.PrivateKey.load_pkcs1(privdat)
        pwd = rsa.decrypt(msg,privkey)
    
    return pwd

def db_connect():
    usr=os.environ.get('DB_USER')
    pwd=base64.b64decode(bytes(os.environ['DB_PWD'],'utf-8'))
    engine=sqlalchemy.create_engine('postgresql://'+usr+':'+pwd_en_de_crypt(pwd,'decrypt').decode('utf8')+'@localhost:5432/stravadata', future=True)
    metadata=sqlalchemy.MetaData(bind=engine)
    return engine, metadata


def location_dict(tbl):
    engine, metadata = db_connect()
    table = sqlalchemy.Table(tbl,metadata,autoload=True,autoload_with=engine, schema='dwh')
    stmt = sqlalchemy.select(table)
    names = []
    ids = []
    with engine.connect() as conn:
        for row in conn.execute(stmt):
            names.append(str(row[1]))
            ids.append(str(row[0]))
    names_dict = dict(zip(names,ids))
    return names_dict

def check_record(tbl,col,rec,eng,metadat):
    table = sqlalchemy.Table(tbl,metadat,autoload=True,autoload_with=eng, schema='dwh')
    stmt1 = sqlalchemy.select(sqlalchemy.func.count()).select_from(table).where(table.c[col].in_(rec))
    stmt2 = sqlalchemy.select(table.c[col])
    lst=[]
    with eng.connect() as conn:
        for r in conn.execute(stmt1):
            cnt=r[0]
        for r in conn.execute(stmt2):            
            lst.append(r[0])
        return cnt, lst
    
def extract_date():
    engine, metadata = db_connect()
    table = sqlalchemy.Table('activity',metadata,autoload=True,autoload_with=engine,schema='dwh')
    stmt = sqlalchemy.select(sqlalchemy.func.max(table.c.start_date)).select_from(table)
    with engine.connect() as conn:
        for row in conn.execute(stmt):
            return row[0]


"""engine = db_connect()
with engine.connect() as conn:
    result = conn.execute(sqlalchemy.text("select 'hello world'"))
    print(result.all())"""

import sqlalchemy
import rsa
import os
import base64
from datetime import datetime
from datetime import time

from sqlalchemy.sql.expression import insert

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


engine, metadata = db_connect()


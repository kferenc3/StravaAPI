import sqlalchemy
import rsa
import os


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

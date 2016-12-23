
DSP = {
   "user"        : "demo",
   "passwd"      : "welcome",
   "ashost"      : "10.68.104.164",
   "sysnr"       : "00",
   "client"      : "620",
   "lang"        : "EN"
}

from platform import system, release
from sys import version_info
from pyrfc import *


conn = Connection(**DSP)
dates = conn.call('BAPI_USER_GET_DETAIL', USERNAME='demo')['LASTMODIFIED']
d = dates['MODDATE']
t = dates['MODTIME']
del conn

conn = Connection(config={'dtime': True}, **DSP)
dates = conn.call('BAPI_USER_GET_DETAIL', USERNAME='demo')['LASTMODIFIED']
dd = dates['MODDATE']
dt = dates['MODTIME']


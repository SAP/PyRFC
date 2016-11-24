
DSP = {
   "user"        : "MM-TECH-01",
   "passwd"      : "mohnmedia",
   # "ashost"      : "coe-he-66",
   "ashost"      : "10.68.104.164",
   "sysnr"       : "00",
   "client"      : "620",
   "lang"        : "EN"
}

from platform import system, release
from sys import version_info
import pyrfc

print 'Platform:', system(), release()
print 'Python version:', version_info
print 'SAP NW RFC:', pyrfc.get_nwrfclib_version()
print 'pyrfc:', pyrfc.__path__

from pyrfc import *

n = 1024

c = Connection(**DSP)

filename = 'rfcexec.exe'

with open(filename, 'rb') as file1: f = file1.read()

content = [{'': bytearray(f[i:i+n])} for i in range(0, len(f), n)]

r = c.call('ZTEST_RAW_TABLE', TT_TBL1024=content)



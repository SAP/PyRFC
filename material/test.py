from platform import system, release
from sys import version_info
from configparser import ConfigParser
from pyrfc import Connection, get_nwrfclib_version

config = ConfigParser()
config.read('pyrfc.cfg')
params = config._sections['test']

conn = Connection(**params)

print(('Platform:', system(), release()))
print(('Python version:', version_info))
print(('SAP NW RFC:', get_nwrfclib_version()))


result = conn.call('/COE/RBP_PAM_SERVICE_ORD_CHANG', IV_ORDERID='4711', IT_NOTICE_NOTIFICATION=[{'': 'ABCD'}, {'': 'XYZ'}])

for line in result['ET_STRING']:
    print(line)

for line in result['ET_TABLE']:
    print(line)

result = conn.call('/COE/RBP_PAM_SERVICE_ORD_CHANG', IV_ORDERID='4711', IT_NOTICE_NOTIFICATION=['ABCD', 'XYZ'])

for line in result['ET_STRING']:
    print(line)

for line in result['ET_TABLE']:
    print(line)


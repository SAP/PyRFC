from platform import system, release
from sys import version_info
from configparser import ConfigParser
from pyrfc import Connection, get_nwrfclib_version

config = ConfigParser()
config.read('tests/pyrfc.cfg')
params = config._sections['coe_he_66'] # or coevi51

conn = Connection(**params)

print('Platform:', system(), release())
print('Python version:', version_info)
print('SAP NW RFC:', get_nwrfclib_version())

PLNTY='A'
PLNNR='00100000'
NOT_REQUESTED = [
  'ET_COMPONENTS',
  'ET_HDR_HIERARCHY',
  'ET_MPACKAGES',
  'ET_OPERATIONS',
  'ET_OPR_HIERARCHY',
  'ET_PRTS',
  'ET_RELATIONS',
]

result = conn.call('EAM_TASKLIST_GET_DETAIL', {'not_requested': NOT_REQUESTED}, IV_PLNTY=PLNTY, IV_PLNNR=PLNNR)
assert len(result['ET_RETURN']) == 0

result = conn.call('EAM_TASKLIST_GET_DETAIL', IV_PLNTY=PLNTY, IV_PLNNR=PLNNR)
assert len(result['ET_RETURN']) == 1

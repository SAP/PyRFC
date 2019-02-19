from platform import system, release
from sys import version_info
from configparser import ConfigParser
from pyrfc import Connection, get_nwrfclib_version

config = ConfigParser()
config.read('tests/pyrfc.cfg')
params = config._sections['coe_he_66']  # or coevi51

conn = Connection(**params)

#print('Platform:', system(), release())
#print('Python version:', version_info)
#print('SAP NW RFC:', get_nwrfclib_version())

COUNT = 99999

result = conn.call('STFC_PERFORMANCE', {'serialize': {
    'ETAB0332': {'batch': 1000, 'callback': 'cb1'},
    'ETAB1000': {'batch': 1000, 'callback': 'cb2'}
}},  **{
    'CHECKTAB': 'X', 'LGET0332': str(COUNT), 'LGET1000': str(COUNT)})
print COUNT, len(result['ETAB0332']), len(result['ETAB1000'])

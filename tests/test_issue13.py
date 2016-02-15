from platform import system, release
from sys import version_info
from configparser import ConfigParser
from pyrfc import Connection, get_nwrfclib_version

config = ConfigParser()
config.read('pyrfc.cfg')
params = config._sections['connection']

conn = Connection(**params)

print('Platform:', system(), release())
print('Python version:', version_info)
print('SAP NW RFC:', get_nwrfclib_version())

input = '0123456789ABCDEF'
L = len(input)
print 'input string:', type(input), len(input), input
r = conn.call('ZPYRFC_TEST_RAW255', IRAW255=input, IXSTR=input)
oraw = r['ORAW255']
oxstr =r['OXSTR']
print 'raw:', type(oraw), len(oraw), oraw
print 'xstr:', type(oxstr), len(oxstr), oxstr

for i in range(0, L):
    print i, type(input[i]), input[i], type(oraw[i]), oraw[i], input[i] == oraw[i], type(oxstr[i]), oxstr[i], input[i] == oxstr[i]

input = bytearray(['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F'])
L = len(input)
print 'input array:', type(input), len(input), input
r = conn.call('ZPYRFC_TEST_RAW255', IRAW255=input, IXSTR=input)
oraw  = bytearray(r['ORAW255'])
oxstr = bytearray(r['OXSTR'])
print 'raw:', type(oraw), len(oraw), oraw
print 'xstr', type(oxstr), len(oxstr), oxstr

for i in range(0, L):
    print i, type(input[i]), input[i], type(oraw[i]), oraw[i], input[i] == oraw[i], type(oxstr[i]), oxstr[i], input[i] == oxstr[i]

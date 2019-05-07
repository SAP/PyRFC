# -*- coding: utf-8 -*-

from pyrfc import Connection

MME = {
    'user': 'demo',
    'passwd': 'welcome',
    'ashost': '10.68.110.51',
    'sysnr': '00',
    'lang': 'EN',
    'client': '620',
    'sysid': 'MME'
}


QI3 = {
    'user': 'BOSKOVIC',
    'passwd': 'Koliko11',
    'ashost': 'ldciqi3.wdf.sap.corp',
    'sysnr': '75',
    'lang': 'EN',
    'client': '005',
    'sysid': 'QI3'
}

ABAP = QI3

conn = Connection(**ABAP)

MAXLEN = 214748364  # 0xCCC CCCC works

LENGTH = MAXLEN  # 0xCCC CCCD fails

try:
    result = conn.call('ZLONG_STRING', IV_COUNT=LENGTH)

    print 'result', \
        LENGTH - len(result['EV_STRING']), \
        LENGTH, result['EV_STRING'][:22]
except Exception as ex:
    print ex

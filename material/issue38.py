connection_info = {
    'user': 'demo',
    'passwd': 'Welcome',
    'ashost': '10.117.19.101',
    'saprouter': '/H/203.13.155.17/W/xjkb3d/H/172.19.138.120/H/',
    'sysnr': '00',
    'lang': 'EN',
    'client': '100',
    'sysid': 'S16'
}

import datetime

from pyrfc import *

conn = Connection(**connection_info)

float_value1 = 1.23456789
float_value2 = 9.87

i = 1

fv = float_value2
if i != 2:
    imp = dict(RFCFLOAT=fv,
                RFCINT2=0x7ffe, RFCINT1=0x7f,
                RFCCHAR4='bcde', RFCINT4=0x7ffffffe,
                RFCHEX3=str.encode('fgh'),
                RFCCHAR1='a', RFCCHAR2='ij',
                RFCTIME='123456',   #datetime.time(12,34,56),
                RFCDATE='20161231', #datetime.date(2011,10,17),
                RFCDATA1='k'*50, RFCDATA2='l'*50
    )
    print('rfc')
    result = conn.call('STFC_STRUCTURE', IMPORTSTRUCT=imp, RFCTABLE=[imp])
    print((fv, result['ECHOSTRUCT']['RFCFLOAT']))


if i == 2:
    print('coe')

    #imp = dict(ZACCP='196602', ZCHAR='ABC', ZCLNT='000', ZCURR=0, ZDATS='', ZDEC=0, ZFLTP=fv, ZSHLP_MAT1='ELIAS')
    imp = dict(ZACCP='196602', ZCHAR='ABC', ZCLNT='620', ZCURR=0, ZDEC=0, ZDATS='19570321', ZFLTP=fv)

    result = conn.call('/COE/RBP_FE_DATATYPES', IV_COUNT=0, IS_INPUT=imp) # ['ES_OUTPUT']
    print((fv, result['ES_OUTPUT']['ZFLTP']))


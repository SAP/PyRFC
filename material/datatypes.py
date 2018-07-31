# -*- coding: utf-8 -*-

connection_info = {
    'user': 'demo',
    'passwd': 'welcome',
    'ashost': '10.68.110.51',
    'sysnr': '00',
    'lang': 'EN',
    'client': '620',
    'sysid': 'MME'
}

from pyrfc import *
from decimal import Decimal

conn = Connection(**connection_info)

is_input = dict(

    # Character
    ZCHAR = u'Hällö SÄP!',
    ZCLNT = '510',
    ZUNIT_DTEL = 'KGM',
    ZCUKY_DTEL = 'USD',
    ZLANG = 'e',

    # Date, time
    ZDATS = '20161231', #datetime.date(2011,10,17),
    ZTIMS = '123456',   #datetime.time(12,34,56),

    # Integer
    ZINT1 = 2 ** 8 - 1,  # 255
    ZINT2 = 2 ** 15 - 1, # 32767
    ZINT4 = 2 ** 31 - 1, # 2147483647

    # Numeric
    ZACCP = '201805',
    ZNUMC = '123456',

    ZPREC = 2,

    # String
    ZRAW = bytes('abc\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'),
    ZRAWSTRING = bytes('四周远处都能望见'),
    ZSTRING = u'\u0001\uf4aa',
    ZSSTRING = u'四周远处都能望见'
)

result = conn.call('/COE/RBP_FE_DATATYPES', IS_INPUT = is_input)['ES_OUTPUT']
for k in is_input:
    if is_input[k] != result[k]:
        print k, type(result[k]) 
        if str(is_input[k]) != str(result[k]):
            print '!', k, is_input[k], result[k]


is_input = dict(
    # Float
    ZFLTP = '0.123456789',

    # Decimal
    ZDEC = '12345.67',

    # Currency, Quantity
    ZCURR = '1234.56',
    ZQUAN = '12.3456',
    ZQUAN_SIGN = '-12.345',    
)

result = conn.call('/COE/RBP_FE_DATATYPES', IS_INPUT = is_input)['ES_OUTPUT']
for key, in_val in is_input.iteritems():
    out_val = result[key]
    if type(in_val) != type(out_val):
        if str(in_val) != str(out_val):
            print 'str:', k, in_val, out_val
    else:
        if in_val != result[key]:
            print key, in_val, out_val

is_input = dict(
# Float
ZFLTP = 0.123456789,

# Decimal
ZDEC = 12345.67,

# Currency, Quantity
ZCURR = 1234.56,
ZQUAN = 12.3456,
ZQUAN_SIGN = -12.345,
)


result = conn.call('/COE/RBP_FE_DATATYPES['ES_OUTPUT']
for key, in_value in is_input.iteritems():
    out_value = result[key]
    if type(in_value) != type(out_value):
        if str(in_value) != str(out_value):
            print 'str:', k, in_value, out_value
    else:
        if in_value != result[key]:
            print key, in_value, out_value

is_input = dict(
# Float
ZFLTP = Decimal('0.123456789'),

# Decimal
ZDEC = Decimal('12345.67'),

# Currency, Quantity
ZCURR = Decimal('1234.56'),
ZQUAN = Decimal('12.3456'),
ZQUAN_SIGN = Decimal('-12.345'),
)


result = conn.call('/COE/RBP_FE_DATATYPES', IS_INPUT = is_input)['ES_OUTPUT']
for key, in_value in is_input.iteritems():
    out_value = result[key]
    if type(in_value) != type(out_value):
        if str(in_value) != str(out_value):
            print 'str:', k, in_value, out_value
    else:
        if in_value != result[key]:
            print key, in_value, out_value

INPUTS = {
    'dec': dict(
        # Float
        ZFLTP = Decimal('0.123456789'),

        # Decimal
        ZDEC = Decimal('12345.67'),

        # Currency, Quantity
        ZCURR = Decimal('1234.56'),
        ZQUAN = Decimal('12.3456'),
        ZQUAN_SIGN = Decimal('-12.345'),
    ),
    
    'numbers': dict(
        # Float
        ZFLTP = 0.123456789,

        # Decimal
        ZDEC = 12345.67,

        # Currency, Quantity
        ZCURR = 1234.56,
        ZQUAN = 12.3456,
        ZQUAN_SIGN = -12.345
    ),

    'strings': dict(
        # Float
        ZFLTP = '0.123456789',

        # Decimal
        ZDEC = '12345.67',

        # Currency, Quantity
        ZCURR = '1234.56',
        ZQUAN = '12.3456',
        ZQUAN_SIGN = '-12.345',    
     )
}

for in_type in INPUTS:
    result = conn.call('/COE/RBP_FE_DATATYPES', IS_INPUT = INPUTS[in_type])['ES_OUTPUT']
    print
    print in_type
    for k in is_input:
        in_val = is_input[k]
        out_val = result[k]
        print k, type(in_val), type(out_val), in_val, out_val
        if type(in_val) != type(out_val):
            assert(str(in_val) == str(out_val))
        else:
            assert(in_val == out_val)
# -*- coding: utf-8 -*-

from abap_systems import DSP
from pyrfc import Connection

function_name = u'ZDT'
# umlauts = u'Hällo SAP!'
umlauts = u'Россия'
# umlauts = u'\u0420\u043e\u0441\u0441\u0438\u044f'

if __name__ == '__main__':
    conn = Connection(**DSP)
    res = conn.call(function_name, IN1=1, MTEXT=umlauts)
    # res = conn.call(function_name, REQUSTR=umlauts, REQUTEXT=umlauts)
    print umlauts
    print res

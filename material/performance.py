# -*- coding: utf-8 -*-

from abap_systems import MME

from pyrfc import Connection

# from memory_profiler import profile

import sys


# @profile
def run(COUNT):
    conn = Connection(**MME)
    result = conn.call('STFC_PERFORMANCE', **{
        'CHECKTAB': 'X', 'LGET0332': str(COUNT), 'LGET1000': str(COUNT)})
    return result


if __name__ == '__main__':
    conn = Connection(**MME)
'''    
    result = conn.call('/COE/RBP_PAM_SERVICE_ORD_CHANG', IV_ORDERID='4711',
                       IT_NOTICE_NOTIFICATION=[{'': 'ABCD'}, {'': 'XYZ'}])
    print(len(result))
    assert len(result['ET_RETURN']) > 0
    erl = result['ET_RETURN'][0]
    assert erl['TYPE'] == 'E'
    assert erl['ID'] == 'IWO_BAPI'
    assert erl['NUMBER'] == '121'
    assert erl['MESSAGE_V1'] == '4711'
'''
COUNT = 99999
for _ in range(10):
    print(_)
    result = run(COUNT)
    print(COUNT, len(result['ETAB0332']), len(result['ETAB1000']))
    print sys.getsizeof(result['ETAB0332'][0]) / 1024, sys.getsizeof(result['ETAB0332']) / 1024, sys.getsizeof(
        result['ETAB0332'][0]) * COUNT / 1024,  sys.getsizeof(result['ETAB0332'][0]) * COUNT - sys.getsizeof(result['ETAB0332'])

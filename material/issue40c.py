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

from pprint import pprint
from pyrfc import Connection

function_name = u'ZHHDEMO_STRUCT_MOD'
#table_name = u'ZHHTT_COL2'
#struct_name = u'ZHHS_COL2'
table_name = u'ZHHT_COL2'
struct_name = u'ZHHS_COL2'


def function_call():
    with Connection(**connection_info) as con:
        return con.call(function_name)


def get_cache():
    with Connection(**connection_info) as con:
        table_cached = con.type_desc_get(table_name)
        struct_cached = con.type_desc_get(struct_name)
        return {
            table_name: vars(table_cached),
            struct_name: vars(struct_cached),
        }


def invalidate():
    with Connection(**connection_info) as con:
        con.func_desc_remove(connection_info['sysid'], function_name)
        con.type_desc_remove(connection_info['sysid'], table_name)
        con.type_desc_remove(connection_info['sysid'], struct_name)


if __name__ == '__main__':
    c1 = get_cache()
    function_call()
    c2 = get_cache()
    invalidate()
    c3 = get_cache()
    pprint(c1)
    assert not c1 == c2 == c3, 'The cache has not changed'

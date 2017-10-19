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

import pyrfc

function_name = u'ZHHDEMO_STRUCT_MOD'
table_name = u'ZHHT_COL2'
struct_name = u'ZHHS_COL2'
field_name = u'COL3'

def get_structure():
    with pyrfc.Connection(**connection_info) as con:
        interface_response = con.call(
            'RFC_GET_FUNCTION_INTERFACE',
            **{'FUNCNAME': function_name}
        )
        assert any(p[u'TABNAME'] == table_name for p in interface_response[u'PARAMS'])
        structure_response = con.call(
            'RFC_GET_STRUCTURE_DEFINITION',
            **{'TABNAME': table_name}
        )
        fields = structure_response[u'FIELDS']
        return [f[u'FIELDNAME'] for f in fields]


def function_call():
    with pyrfc.Connection(**connection_info) as con:
        return con.call(function_name)

def invalidate():
    with pyrfc.Connection(**connection_info) as con:
        con.func_desc_remove(connection_info['sysid'], function_name)
        con.type_desc_remove(connection_info['sysid'], table_name)
        con.type_desc_remove(connection_info['sysid'], struct_name)
        #con.reset_server_context()

if __name__ == '__main__':
    print('STRUCTURE 1', get_structure())
    print('RESULT 1', function_call())
    raw_input('Structure changed now. Press Enter to continue...')
    invalidate()
    print('STRUCTURE 2', get_structure())
    print('RESULT 2', function_call())

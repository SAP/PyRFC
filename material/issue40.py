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

def get_structure(con):
    type_desc = con.type_desc_get(struct_name)
    return any (field['name'] == field_name for field in type_desc.fields)

def function_call(con):
    table = con.call(function_name)['EX_ZHHT_COL2']
    struct = table[0]
    return field_name in struct.keys()

def invalidate(con):
    con.func_desc_remove(connection_info['sysid'], function_name)
    con.type_desc_remove(connection_info['sysid'], table_name)
    con.type_desc_remove(connection_info['sysid'], struct_name)
    #con.reset_server_context()
    #con.type_desc_remove('DSP', type_name)
    #con.reopen()

if __name__ == '__main__':
    c1 = pyrfc.Connection(**connection_info)
    print 'STRUCTURE', get_structure(c1) #, 'RFC', function_call(c1)
    raw_input('Structure changed now. Press Enter to continue...')
    invalidate(c1)
    print 'STRUCTURE', get_structure(c1) #, 'RFC', function_call(c1)

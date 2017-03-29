import pyrfc

backend = {
    'user': 'demo',
    'passwd': 'welcome',
    'ashost': ' 10.117.19.101',
    'saprouter': '/H/203.13.155.17/W/xjkb3d/H/172.19.138.120/H/',
    'sysnr': '00',
    'lang': 'EN',
    'client': '100'
}
def get_error(ex):
    error = {}
    ex_type_full = str(type(ex))
    error['type'] = ex_type_full[ex_type_full.rfind(".")+1:ex_type_full.rfind("'")]
    error['code'] = ex.code if hasattr(ex, 'code') else '<None>'
    error['key'] = ex.key if hasattr(ex, 'key') else '<None>'
    error['message'] = ex.message.split("\n")
    error['msg_class'] = ex.msg_class if hasattr(ex, 'msg_class') else '<None>'
    error['msg_type'] = ex.msg_type if hasattr(ex, 'msg_type') else '<None>'
    error['msg_number'] = ex.msg_number if hasattr(ex, 'msg_number') else '<None>'
    error['msg_v1'] = ex.msg_v1 if hasattr(ex, 'msg_v1') else '<None>'
    return error

conn = pyrfc.Connection(**backend)

# put in cache
result = conn.call('BAPI_USER_GET_DETAIL', USERNAME="DEMO")

# get from cache
fd = conn.func_desc_get_cached('S16', 'BAPI_USER_GET_DETAIL')
assert fd.__class__ is pyrfc._pyrfc.FunctionDescription

# remove from cache
conn.func_desc_remove('S16', 'BAPI_USER_GET_DETAIL')
try:
    fd = conn.func_desc_get_cached('S16', 'BAPI_USER_GET_DETAIL')
    assert fd.__class__ is not 'pyrfc._pyrfc.FunctionDescription'
except pyrfc.RFCError as ex:
    error = get_error(ex)
    assert error['code'] == 17
    assert error['key'] == 'RFC_NOT_FOUND'


try:
    from configparser import ConfigParser
    COPA = ConfigParser()
except ImportError as ex:
    COPA = config_parser()
    from configparser import config_parser

COPA.read('tests/pyrfc.cfg')
CONFIG_SECTIONS = COPA._sections
PARAMS = CONFIG_SECTIONS['coevi51']
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

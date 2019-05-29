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

ABAP = MME

RFM = '/coe/rbp_fe_datatypes'
BAPI = 'BAPI_PERSDATANL_CREATE'
STRUCTURE = '/COE/RBP_S_FE_RFM_STRUCTURE'
STR_INCLUDE = 'bapi_shp_material'
TABLE = '/COE/RBP_T_FE_RFM_TABLE_TYPE'

conn = Connection(**ABAP)


def rfm(name):
    rfm = conn.get_function_description(RFM)
    for p in rfm.parameters:
        print p['direction'], p['optional']
        if p['type_description'] is None:
            field = '%s: %s %u' % (
                p['name'], p['parameter_type'], p['uc_length'])
            if p['parameter_type'] in ['RFCTYPE_NUM', 'RFCTYPE_BCD', 'RFCTYPE_FLOAT']:
                field += '.%u' % p['decimals']
            print field
        else:
            for f in p['type_description'].fields:
                field = '%s: %s %u' % (
                    f['name'], f['field_type'], f['uc_length'])
                if f['field_type'] in ['RFCTYPE_NUM', 'RFCTYPE_BCD', 'RFCTYPE_FLOAT']:
                    field += '.%u' % f['decimals']
                print field
        print


if __name__ == "__main__":
    rfm(RFM)

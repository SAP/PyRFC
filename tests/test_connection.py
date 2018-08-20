#!/usr/bin/env python
# -*- coding: utf-8 -*-

from decimal import Decimal
import datetime
import pyrfc
import socket

import pytest

from tests.config import PARAMS as params, CONFIG_SECTIONS as config_sections, get_error


class TestConnection():

    def setup_method(self, test_method):
        self.conn = pyrfc.Connection(**params)
        assert self.conn.alive

    def test_version(self):
        with open('VERSION', 'r') as f:
            VERSION = f.read().strip()
        assert pyrfc.__version__ == VERSION

    def test_info(self):
        connection_info = self.conn.get_connection_attributes()
        assert connection_info['isoLanguage'] == u'EN'

    def teardown_method(self, test_method):
        self.conn.close()
        assert not self.conn.alive

    # todo: test correct status after error -> or to the error tests?
    def test_incomplete_params(self):
        incomplete_params = params.copy()
        for p in ['ashost', 'gwhost', 'mshost']:
            if p in incomplete_params:
                del incomplete_params[p]
        try:
            pyrfc.Connection(**incomplete_params)
        except pyrfc.RFCError as ex:
            error = get_error(ex)
        assert error['code'] == 20
        assert error['key'] == 'RFC_INVALID_PARAMETER'
        assert error['message'][0] in ['Parameter ASHOST, GWHOST, MSHOST or SERVER_PORT is missing.',
                                       'Parameter ASHOST, GWHOST or MSHOST is missing.']

    def test_denied_users(self):
        denied_params = params.copy()
        denied_params['user'] = 'BLAFASEL'
        try:
            pyrfc.Connection(**denied_params)
        except pyrfc.LogonError as ex:
            error = get_error(ex)

        assert error['code'] == 2
        assert error['key'] == 'RFC_LOGON_FAILURE'
        assert error['message'][0] == 'Name or password is incorrect (repeat logon)'

    def test_config_parameter(self):
        # rstrip test
        conn = pyrfc.Connection(
            config={'rstrip': False}, **config_sections['coevi51'])
        hello = u'Hällo SAP!' + u' ' * 245
        result = conn.call('STFC_CONNECTION', REQUTEXT=hello)
        # Test with rstrip=False (input length=255 char)
        assert result['ECHOTEXT'] == hello
        result = conn.call('STFC_CONNECTION', REQUTEXT=hello.rstrip())
        # Test with rstrip=False (input length=10 char)
        assert result['ECHOTEXT'] == hello
        conn.close()
        # dtime test
        conn = pyrfc.Connection(
            config={'dtime': True}, **config_sections['coevi51'])
        dates = conn.call('BAPI_USER_GET_DETAIL', USERNAME='demo')[
            'LASTMODIFIED']
        assert type(dates['MODDATE']) is datetime.date
        assert type(dates['MODTIME']) is datetime.time
        del conn
        conn = pyrfc.Connection(**config_sections['coevi51'])
        dates = conn.call('BAPI_USER_GET_DETAIL', USERNAME='demo')[
            'LASTMODIFIED']
        assert type(dates['MODDATE']) is not datetime.date
        assert type(dates['MODDATE']) is not datetime.time
        del conn
        # no import params return
        result = self.conn.call('STFC_CONNECTION', REQUTEXT=hello)
        assert 'REQTEXT' not in result
        # return import params
        conn = pyrfc.Connection(
            config={'return_import_params': True}, **config_sections['coevi51'])
        result = conn.call('STFC_CONNECTION', REQUTEXT=hello.rstrip())
        assert hello.rstrip() == result['REQUTEXT']
        conn.close()

    def test_ping(self):
        self.conn.ping()

    def test_call_undefined(self):
        try:
            self.conn.call('undefined')
        except pyrfc.ABAPApplicationError as ex:
            error = get_error(ex)
        assert error['code'] == 5
        assert error['key'] == 'FU_NOT_FOUND'
        assert error['message'][0] == 'ID:FL Type:E Number:046 undefined'

        try:
            self.conn.call('STFC_CONNECTION', undefined=0)
        except pyrfc.ExternalRuntimeError as ex:
            error = get_error(ex)
        assert error['code'] == 20
        assert error['key'] == 'RFC_INVALID_PARAMETER'
        assert error['message'][0] == "field 'undefined' not found"

    def test_date_output(self):
        lm = self.conn.call('BAPI_USER_GET_DETAIL', USERNAME='demo')[
            'LASTMODIFIED']
        assert len(lm['MODDATE']) > 0
        assert len(lm['MODTIME']) > 0

    def test_connection_attributes(self):
        data = self.conn.get_connection_attributes()
        assert data['client'] == str(params['client'])
        assert data['host'] == str(socket.gethostname())
        assert data['isoLanguage'] == str(params['lang'].upper())
        # Only valid for direct logon systems:
        # self.assertEqual(data['sysNumber'], str(params['sysnr']))
        assert data['user'] == str(params['user'].upper())
        assert data['rfcRole'] == u'C'

    def test_not_requested(self):
        PLNTY = 'A'
        PLNNR = '00100000'
        NOT_REQUESTED = [
            'ET_COMPONENTS',
            'ET_HDR_HIERARCHY',
            'ET_MPACKAGES',
            'ET_OPERATIONS',
            'ET_OPR_HIERARCHY',
            'ET_PRTS',
            'ET_RELATIONS',
        ]
        result = self.conn.call('EAM_TASKLIST_GET_DETAIL', {
                                'not_requested': NOT_REQUESTED}, IV_PLNTY=PLNTY, IV_PLNNR=PLNNR)
        assert len(result['ET_RETURN']) == 0
        result = self.conn.call('EAM_TASKLIST_GET_DETAIL',
                                IV_PLNTY=PLNTY, IV_PLNNR=PLNNR)
        assert len(result['ET_RETURN']) == 1

    def test_datatypes(self):
        INPUTS = [dict(
            # Float
            ZFLTP=0.123456789,

            # Decimal
            ZDEC=12345.67,

            # Currency, Quantity
            ZCURR=1234.56,
            ZQUAN=12.3456,
            ZQUAN_SIGN=-12.345
        ),

            dict(
            # Float
            ZFLTP=Decimal('0.123456789'),

            # Decimal
            ZDEC=Decimal('12345.67'),

            # Currency, Quantity
            ZCURR=Decimal('1234.56'),
            ZQUAN=Decimal('12.3456'),
            ZQUAN_SIGN=Decimal('-12.345'),
        ),

            dict(
            # Float
            ZFLTP='0.123456789',

            # Decimal
            ZDEC='12345.67',

            # Currency, Quantity
            ZCURR='1234.56',
            ZQUAN='12.3456',
            ZQUAN_SIGN='-12.345',
        )]

        for is_input in INPUTS:
            result = self.conn.call(
                '/COE/RBP_FE_DATATYPES', IS_INPUT=is_input)['ES_OUTPUT']
            for k in is_input:
                in_value = is_input[k]
                out_value = result[k]
                if k == 'ZFLTP':
                    assert(type(out_value) is float)
                else:
                    assert(type(out_value) is Decimal)
                if type(in_value) != type(out_value):
                    assert(str(in_value) == str(out_value))
                else:
                    assert(in_value == out_value)


'''
    def test_many_connections(self):
        # If too many connections are established, the following error will occur (on interactive python shell)
        #
        #CommunicationError: Error 1: [RFC_COMMUNICATION_FAILURE]
        #LOCATION    CPIC (TCP/IP) on local host with Unicode
        #ERROR       max no of 100 conversations exceeded
        #TIME        Tue Sep 18 11:09:35 2012
        #RELEASE     720
        #COMPONENT   CPIC (TCP/IP) with Unicode
        #VERSION     3
        #RC          466
        #MODULE      r3cpic_mt.c
        #LINE        14345
        #COUNTER     1
        # ABAP:
        for i in range(101):
            conn2 = pyrfc.Connection(**params)
            # conn2.close() # Use explicit close() here. If ommitted, the server may block an open connection attempt
                          # _and refuse further connections_, resulting in RFC_INVALID_HANDLE errors for the other
                          # test!


# old tests, referring to non static z-functions
#    def test_invalid_input(self):
#        self.conn.call('Z_PBR_EMPLOYEE_GET', IV_EMPLOYEE='100190', IV_USER_ID='')
#        self.conn.call('Z_PBR_EMPLOYEE_GET', IV_EMPLOYEE='', IV_USER_ID='HRPB_MNG01')
#        self.assertRaises(TypeError, self.conn.call, 'Z_PBR_EMPLOYEE_GET', IV_EMPLOYEE=100190, IV_USER_ID='HRPB_MNG01')
#
#    def test_xstring_output(self):
#        self.conn.call('Z_PBR_EMPLOYEE_GET_XSTRING', IV_EMPLOYEE='100190')
#
#    def test_xstring_input_output(self):
#        for i in 1, 2, 3, 1023, 1024, 1025:
#            s = 'X' * i
#            out = self.conn.call('Z_PBR_TEST_2', IV_INPUT_XSTRING=s)
#            self.assertEqual(s, out['EV_EXPORT_XSTRING'])

'''
if __name__ == '__main__':
    unittest.main()

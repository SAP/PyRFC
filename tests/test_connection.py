#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime, pyrfc, unittest, socket, timeit
from ConfigParser import ConfigParser

config = ConfigParser()
config.read('pyrfc.cfg')
params = config._sections['connection']

class ConnectionTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.conn = pyrfc.Connection(**params)
        # Assure english as connection language
        connection_info = cls.conn.get_connection_attributes()
        if connection_info['isoLanguage'] != u'EN':
            raise pyrfc.RFCError("Testing must be done with English as language.")

    @classmethod
    def tearDownClass(cls):
        pass

    # TODO: test correct status after error -> or to the error tests?

    def test_incomplete_params(self):
        incomplete_params = params.copy()
        for p in ['ashost', 'gwhost', 'mshost']:
            if p in incomplete_params:
                del incomplete_params[p]
        with self.assertRaises(pyrfc.ExternalRuntimeError) as run:
            pyrfc.Connection(**incomplete_params)
        self.assertEqual(run.exception.code, 20)
        self.assertEqual(run.exception.key, 'RFC_INVALID_PARAMETER')
        self.assertEqual(run.exception.message, 'Parameter ASHOST, GWHOST or MSHOST is missing.')

    def test_denied_users(self):
        denied_params = params.copy()
        denied_params['user'] = 'BLAFASEL'
        with self.assertRaises(pyrfc.LogonError) as run:
            pyrfc.Connection(**denied_params)
        self.assertEqual(run.exception.code, 2)
        self.assertEqual(run.exception.key, 'RFC_LOGON_FAILURE')
        self.assertEqual(run.exception.message, 'Name or password is incorrect (repeat logon)')

    def test_config_parameter(self):
        # rstrip test
        conn2 = pyrfc.Connection(config={'rstrip': False}, **config._sections['connection'])
        hello = u'Hällo SAP!' + u' ' * 245
        result = conn2.call('STFC_CONNECTION', REQUTEXT=hello)
        self.assertEqual(result['ECHOTEXT'], hello, "Test with rstrip=False (input length=255 char)")
        result = conn2.call('STFC_CONNECTION', REQUTEXT=hello.rstrip())
        self.assertEqual(result['ECHOTEXT'], hello, "Test with rstrip=False (input length=10 char)")
        conn2.close()

        # return_import_params
        result = self.conn.call('STFC_CONNECTION', REQUTEXT=hello)
        with self.assertRaises(KeyError):
            imp_var = result['REQUTEXT']
        conn3 = pyrfc.Connection(config={'return_import_params': True}, **config._sections['connection'])
        result = conn3.call('STFC_CONNECTION', REQUTEXT=hello.rstrip())
        imp_var = result['REQUTEXT']
        conn3.close()


    @unittest.skip("time consuming; may block other tests")
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
        for i in range(150):
            conn2 = pyrfc.Connection(**params)
            conn2.close() # Use explicit close() here. If ommitted, the server may block an open connection attempt
                          # _and refuse further connections_, resulting in RFC_INVALID_HANDLE errors for the other
                          # test!

    def test_ping(self):
        self.conn.ping()

    def test_call_undefined(self):
        with self.assertRaises(pyrfc.ABAPApplicationError) as run:
            self.conn.call('undefined')
        self.assertEqual(run.exception.code, 5)
        self.assertEqual(run.exception.key, 'FU_NOT_FOUND')
        self.assertEqual(run.exception.message, 'ID:FL Type:E Number:046 undefined')
        with self.assertRaises(pyrfc.ExternalRuntimeError) as run:
            self.conn.call('STFC_CONNECTION', undefined=0)
        self.assertEqual(run.exception.code, 20)
        self.assertEqual(run.exception.key, 'RFC_INVALID_PARAMETER')
        self.assertEqual(run.exception.message, "field 'undefined' not found")


    def test_date_output(self):
        self.conn.call('BAPI_USER_GET_DETAIL', USERNAME='mc_test')


    def test_connection_attributes(self):
        data = self.conn.get_connection_attributes()
        self.assertEquals(data['client'], unicode(params['client']))
        self.assertEquals(data['host'], unicode(socket.gethostname()))
        self.assertEquals(data['isoLanguage'], unicode(params['lang'].upper()))
        # Only valid for direct logon systems:
        # self.assertEquals(data['sysNumber'], unicode(params['sysnr']))
        self.assertEquals(data['user'], unicode(params['user'].upper()))
        self.assertEquals(data['rfcRole'], u'C')

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

if __name__ == '__main__':
    unittest.main()


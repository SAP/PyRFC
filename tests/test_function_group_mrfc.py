#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: Some test cases for the exception testing are taken from the c-connector test cases
# /bas/BIN/src/krn/rfc/nwrfc/testFramework/clienttests/ExceptionTest.c
# Furthermore, the python script error_test.py in this directory provides more test cases.
# Some of them are used as well.

import datetime
import pyrfc
import socket

import pytest

from tests.config import PARAMS as params, CONFIG_SECTIONS as config_sections, get_error


class TestMRFC():
    """
    This test cases cover selected functions from the MRFC function group.
    """

    def setup_method(self, test_method):
        self.conn = pyrfc.Connection(**params)
        assert self.conn.alive

    def test_info(self):
        connection_info = self.conn.get_connection_attributes()
        assert connection_info['isoLanguage'] == u'EN'

    def teardown_method(self, test_method):
        self.conn.close()
        assert not self.conn.alive

    '''
    @unittest.skip("not remote-enabled")
    def test_ABAP4_CALL_TRANSACTION_VB(self):
        # ABAP4_CALL_TRANSACTION_VB
        pass

    @unittest.skip("not remote-enabled")
    def test_IS_VERIRUN_ACTIVE(self):
        # IS_VERIRUN_ACTIVE Determine Whether a Verification Run is Active
        pass

    @unittest.skip("not supported yet (trfc)")
    def test_RFC_CALL_TRANSACTION_USING(self):
        # RFC_CALL_TRANSACTION_USING Verification Program for Execution of RFCs via CALL TRANSACTION USING
        pass

    # ToDo: Class based exceptions
    def test_RFC_CLASS_BASED_EXCP(self):
        # RFC_CLASS_BASED_EXCP RFC mit klassenbasierten Exceptions
        pass

    # TODO: How to test?
    @unittest.skip("not supported yet")
    def test_RFC_PING_AND_WAIT(self):
       # RFC_PING_AND_WAIT Aufruf und Warten
        pass
    '''

    def test_RFC_RAISE_ERROR_AbapApplicationError(self):
        # Comment: cf. result_print of the error_test.py
        # '1_E': 'ABAPApplicationError-5-RAISE_EXCEPTION-ID:SR Type:E Number:006 STRING-True',
        # cf. ExceptionTest.c (l. 75ff)
        try:
            self.conn.call('RFC_RAISE_ERROR', METHOD='1', MESSAGETYPE='E')
        except pyrfc.ABAPApplicationError as ex:
            error = get_error(ex)
            assert error['code'] == 5
            assert error['key'] == 'RAISE_EXCEPTION'
            assert error['msg_class'] == u'SR'
            assert error['msg_type'] == 'E'
            assert error['msg_number'] == '006'
            # Assures that the connection handle is correctly synchronized
            self.conn.call('RFC_PING')

        # '2_E': 'ABAPApplicationError-5-RAISE_EXCEPTION- Number:000-True',
        # cf. ExceptionTest.c (l. 65ff)
        try:
            self.conn.call('RFC_RAISE_ERROR', METHOD='2', MESSAGETYPE='E')
        except pyrfc.ABAPApplicationError as ex:
            error = get_error(ex)
            assert error['code'] == 5
            assert error['key'] == 'RAISE_EXCEPTION'
            assert error['msg_number'] == '006'
            self.conn.call('RFC_PING')

    def test_RFC_RAISE_ERROR_AbapRuntimeError(self):
        # RFC_RAISE_ERROR ARFC: Raise Different Type of Error Message
        # Comment: cf. result_print of the error_test.py
        # cf. ExceptionTest.c (l. 92ff)
        try:
            self.conn.call('RFC_RAISE_ERROR', METHOD='0', MESSAGETYPE='E')
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error['code'] == 4
            assert error['message'][0] == u'Function not supported'
            self.conn.call('RFC_PING')

        # cf. ExceptionTest.c (l. 112ff)
        try:
            self.conn.call('RFC_RAISE_ERROR', MESSAGETYPE='A')
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error['code'] == 4
            assert error['msg_class'] == 'SR'
            assert error['msg_type'] == 'A'
            assert error['msg_number'] == '006'
            assert error['msg_v1'] == 'Method = 0'
            self.conn.call('RFC_PING')

        # cf. ExceptionTest.c (l. 137ff)
        try:
            self.conn.call('RFC_RAISE_ERROR', MESSAGETYPE='X')
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error['code'] == 4
            assert error['key'] == 'MESSAGE_TYPE_X'
            assert error['msg_class'] == '00'
            assert error['msg_type'] == 'X'
            assert error['msg_number'] == '341'
            assert error['msg_v1'] == 'MESSAGE_TYPE_X'
            self.conn.call('RFC_PING')

        # '36_E': 'ABAPRuntimeError-4-Division by 0 (type I)-Division by 0 (type I)-True''] ==
        try:
            self.conn.call('RFC_RAISE_ERROR', METHOD='36', MESSAGETYPE='E')
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error['code'] == 4
            assert u'Division by 0' in error['message'][0]
            self.conn.call('RFC_PING')

        # '3_E': 'ABAPRuntimeError-3-COMPUTE_INT_ZERODIVIDE-Division by 0 (type I)-True''] ==
        # cf. ExceptionTest.c (l. 164ff)
        try:
            self.conn.call('RFC_RAISE_ERROR', METHOD='3', MESSAGETYPE='E')
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error['code'] == 3
            assert error['key'] == 'COMPUTE_INT_ZERODIVIDE'
            self.conn.call('RFC_PING')

        # '51_E': 'ABAPRuntimeError-3-BLOCKED_COMMIT-A database commit was blocked by the application.-True''] ==
        try:
            self.conn.call('RFC_RAISE_ERROR', METHOD='51', MESSAGETYPE='E')
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error['code'] == 3
            assert error['key'] == 'BLOCKED_COMMIT'
            self.conn.call('RFC_PING')

    ''' todo Windows test crashes!
    def test_RFC_RAISE_ERROR_ExternalRuntimeError(self):
        # Comment: cf. result_print of the error_test.py
        # '11_E': 'ExternalRuntimeError-17-RFC_NOT_FOUND-Function RFCPING not found-True',
        try:
            self.conn.call('RFC_RAISE_ERROR', METHOD='11', MESSAGETYPE='E')
        #except (pyrfc.ExternalRuntimeError) as ex:
        except (Exception) as ex:
            assert True
            #error = get_error(ex)
            #assert error['code'] == 17
            #assert error['key'] == 'RFC_NOT_FOUND'
            #self.conn.call('RFC_PING')
    '''
    # def test_RFC_RAISE_ERROR_CommunicationError(self):
    # Comment: cf. result_print of the error_test.py
    # '32_E': 'CommunicationError-1-RFC_COMMUNICATION_FAILURE-connection closed without message (CM_NO_DATA_RECEIVED)-True',
    # try:
    ##    self.conn.call('RFC_RAISE_ERROR', METHOD='32', MESSAGETYPE='E')
    # except (pyrfc.ABAPRuntimeError) as ex:
    #    error = get_error(ex)
    #    assert error['code'] == 4
    #    assert error['key'] == 'ON:N'
    # except (pyrfc.CommunicationError) as ex:
    ##    error = get_error(ex)
    ##    assert error['code'] == 1
    ##    assert error['key'] == 'RFC_COMMUNICATION_FAILURE'
    # self.conn.call('RFC_PING')
    '''
    @unittest.skip("not remote-enabled")
    def test_RFC_RAISE_ERROR_VB(self):
        # RFC_RAISE_ERROR_VB Behandlung von RFC-Methoden in Verbuchung
        pass

    def test_RFC_TRANSFER_TABLE(self):
        # RFC_TRANSFER_TABLE RFC Test:   PERFORMANCE Test
#         Table input
        pass
#In [45]: h332 = [{'LINE1': 'Hallo', 'LINE2': 'Lise', 'LINE3': 'lauft', 'LINE4': 'leise'}, {'LINE1': 'Hallo', 'LINE2': 'aLise', 'LINE3': 'alauft', 'LINE4': 'aleise'}]
#In [46]: h1000 = [{'LINE1': 'Hallo', 'LINE2': 'Lise', 'LINE3': 'lauft', 'LINE4': 'leise', 'LINE5':'und fuenf'}, {'LINE1': 'Hallo', 'LINE2': 'aLise', 'LINE3': 'alauft', 'LINE4': 'aleise', 'LINE5': 'und sechs'}]
#In [47]: result = conn.call('RFC_TRANSFER_TABLE', APPEND=1, CHECKTAB='y', IMP0332=h332, IMP1000=h1000)


    @unittest.skip("not supported yet (xml)")
    def test_RFC_XML_TEST_1(self):
        # RFC_XML_TEST_1 Test xml stream
        pass

    '''

    def test_STFC_CHANGING(self):
        # STFC_CHANGING example with CHANGING parameters
        start_value = 33
        counter = 88
        result = self.conn.call(
            'STFC_CHANGING', START_VALUE=start_value, COUNTER=counter)
        assert result['COUNTER'] == counter + 1
        assert result['RESULT'] == start_value + counter


if __name__ == '__main__':
    unittest.main()

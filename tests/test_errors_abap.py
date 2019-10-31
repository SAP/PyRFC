#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import socket
import unittest
import pyrfc

from decimal import Decimal
from tests.config import PARAMS as params, CONFIG_SECTIONS as config_sections, get_error


class TestConnection:
    def setup_method(self, test_method):
        self.conn = pyrfc.Connection(**params)
        assert self.conn.alive

    def teardown_method(self, test_method):
        self.conn.close()
        assert not self.conn.alive

    def test_no_connection_params(self):
        try:
            pyrfc.Connection()
        except pyrfc.RFCError as ex:
            assert ex.args[0] == "Connection parameters missing"

    def test_RFC_RAISE_ERROR(self):
        try:
            result = self.conn.call("RFC_RAISE_ERROR", MESSAGETYPE="A")
        except pyrfc.ABAPRuntimeError as ex:
            assert ex.code == 4
            assert ex.key == "Function not supported"
            assert ex.message == "Function not supported"
            assert ex.msg_class == "SR"
            assert ex.msg_type == "A"
            assert ex.msg_number == "006"

    def test_STFC_SAPGUI(self):
        # STFC_SAPGUI RFC-TEST:   RFC with SAPGUI
        try:
            self.conn.call("STFC_SAPGUI")
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error["code"] == 3
            assert error["key"] == "DYNPRO_SEND_IN_BACKGROUND"

    def test_RFC_RAISE_ERROR_AbapRuntimeError_E0(self):
        # RFC_RAISE_ERROR ARFC: Raise Different Type of Error Message
        # Comment: cf. result_print of the error_test.py
        # cf. ExceptionTest.c (l. 92ff)
        try:
            self.conn.call("RFC_RAISE_ERROR", METHOD="0", MESSAGETYPE="E")
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error["code"] == 4
            assert error["message"][0] == u"Function not supported"
            self.conn.call("RFC_PING")

    def test_RFC_RAISE_ERROR_AbapApplicationError_E1(self):
        # Comment: cf. result_print of the error_test.py
        # '1_E': 'ABAPApplicationError-5-RAISE_EXCEPTION-ID:SR Type:E Number:006 STRING-True',
        # cf. ExceptionTest.c (l. 75ff)
        try:
            self.conn.call("RFC_RAISE_ERROR", METHOD="1", MESSAGETYPE="E")
        except pyrfc.ABAPApplicationError as ex:
            error = get_error(ex)
            assert error["code"] == 5
            assert error["key"] == "RAISE_EXCEPTION"
            assert error["msg_class"] == u"SR"
            assert error["msg_type"] == "E"
            assert error["msg_number"] == "006"
            # Assures that the connection handle is correctly synchronized
            self.conn.call("RFC_PING")

    def test_RFC_RAISE_ERROR_AbapApplicationError_E2(self):
        # '2_E': 'ABAPApplicationError-5-RAISE_EXCEPTION- Number:000-True',
        # cf. ExceptionTest.c (l. 65ff)
        try:
            self.conn.call("RFC_RAISE_ERROR", METHOD="2", MESSAGETYPE="E")
        except pyrfc.ABAPApplicationError as ex:
            error = get_error(ex)
            assert error["code"] == 5
            assert error["key"] == "RAISE_EXCEPTION"
            assert error["msg_number"] == "000"
            self.conn.call("RFC_PING")

    def test_RFC_RAISE_ERROR_AbapRuntimeError_E3(self):
        # '3_E': 'ABAPRuntimeError-3-COMPUTE_INT_ZERODIVIDE-Division by 0 (type I)-True''] ==
        # cf. ExceptionTest.c (l. 164ff)
        try:
            self.conn.call("RFC_RAISE_ERROR", METHOD="3", MESSAGETYPE="E")
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error["code"] == 3
            assert error["key"] == "COMPUTE_INT_ZERODIVIDE"
            self.conn.call("RFC_PING")

    def test_RFC_RAISE_ERROR_AbapRuntimeError_A(self):
        # cf. ExceptionTest.c (l. 112ff)
        try:
            self.conn.call("RFC_RAISE_ERROR", MESSAGETYPE="A")
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error["code"] == 4
            assert error["msg_class"] == "SR"
            assert error["msg_type"] == "A"
            assert error["msg_number"] == "006"
            assert error["msg_v1"] == "Method = 0"
            self.conn.call("RFC_PING")

    def test_RFC_RAISE_ERROR_AbapRuntimeError_X(self):
        # cf. ExceptionTest.c (l. 137ff)
        try:
            self.conn.call("RFC_RAISE_ERROR", MESSAGETYPE="X")
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error["code"] == 4
            assert error["key"] == "MESSAGE_TYPE_X"
            assert error["msg_class"] == "00"
            assert error["msg_type"] == "X"
            assert error["msg_number"] == "341"
            assert error["msg_v1"] == "MESSAGE_TYPE_X"
            self.conn.call("RFC_PING")

    def test_RFC_RAISE_ERROR_AbapRuntimeError_E36(self):
        # '36_E': 'ABAPRuntimeError-4-Division by 0 (type I)-Division by 0 (type I)-True''] ==
        try:
            self.conn.call("RFC_RAISE_ERROR", METHOD="36", MESSAGETYPE="E")
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error["code"] == 4
            assert u"Division by 0" in error["message"][0]
            self.conn.call("RFC_PING")

    def test_RFC_RAISE_ERROR_AbapRuntimeError_E51(self):
        # '51_E': 'ABAPRuntimeError-3-BLOCKED_COMMIT-A database commit was blocked by the application.-True''] ==
        try:
            self.conn.call("RFC_RAISE_ERROR", METHOD="51", MESSAGETYPE="E")
        except (pyrfc.ABAPRuntimeError) as ex:
            error = get_error(ex)
            assert error["code"] == 3
            assert error["key"] == "BLOCKED_COMMIT"
            self.conn.call("RFC_PING")

    """ todo Windows test crashes!
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
    """
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


if __name__ == "__main__":
    unittest.main()

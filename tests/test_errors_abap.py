#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

import pytest
from pyrfc import (
    Connection,
    RFCError,
    ABAPRuntimeError,
    ABAPApplicationError,
    # CommunicationError,
    # ExternalRuntimeError,
)

from tests.config import PARAMS as params


class TestErrorsABAP:
    def setup_method(self):
        self.conn = Connection(**params)
        assert self.conn.alive

    def teardown_method(self):
        self.conn.close()
        assert not self.conn.alive

    def test_no_connection_params(self):
        with pytest.raises(RFCError) as ex:
            Connection()
        error = ex.value
        assert error.args[0] == "Connection parameters missing"

    def test_RFC_RAISE_ERROR(self):
        with pytest.raises(ABAPRuntimeError) as ex:
            self.conn.call("RFC_RAISE_ERROR", MESSAGETYPE="A")
        assert self.conn.alive is True
        error = ex.value
        assert error.code == 4
        assert error.key == "Function not supported"
        assert error.message == "Function not supported"
        assert error.msg_class == "SR"
        assert error.msg_type == "A"
        assert error.msg_number == "006"

    def test_STFC_SAPGUI(self):
        # STFC_SAPGUI RFC-TEST:   RFC with SAPGUI
        with pytest.raises(ABAPRuntimeError) as ex:
            self.conn.call("STFC_SAPGUI")
        assert self.conn.alive is True
        error = ex.value
        assert error.code == 3
        assert error.key == "DYNPRO_SEND_IN_BACKGROUND"

    def test_RFC_RAISE_ERROR_AbapRuntimeError_E0(self):
        # RFC_RAISE_ERROR ARFC: Raise Different Type of Error Message
        # Comment: cf. result_print of the error_test.py
        # cf. ExceptionTest.c (l. 92ff)
        with pytest.raises(ABAPRuntimeError) as ex:
            self.conn.call("RFC_RAISE_ERROR", METHOD="0", MESSAGETYPE="E")
        error = ex.value
        assert self.conn.alive is True
        assert error.code == 4
        assert error.message == "Function not supported"

    def test_RFC_RAISE_ERROR_AbapApplicationError_E1(self):
        # Comment: cf. result_print of the error_test.py
        # '1_E': 'ABAPApplicationError-5-RAISE_EXCEPTION-ID:SR Type:E Number:006 STRING-True',
        # cf. ExceptionTest.c (l. 75ff)
        with pytest.raises(ABAPApplicationError) as ex:
            self.conn.call("RFC_RAISE_ERROR", METHOD="1", MESSAGETYPE="E")
        assert self.conn.alive is True
        error = ex.value
        assert error.code == 5
        assert error.key == "RAISE_EXCEPTION"
        assert error.msg_class == "SR"
        assert error.msg_type == "E"
        assert error.msg_number == "006"

    def test_RFC_RAISE_ERROR_AbapApplicationError_E2(self):
        # '2_E': 'ABAPApplicationError-5-RAISE_EXCEPTION- Number:000-True',
        # cf. ExceptionTest.c (l. 65ff)
        with pytest.raises(ABAPApplicationError) as ex:
            self.conn.call("RFC_RAISE_ERROR", METHOD="2", MESSAGETYPE="E")
        assert self.conn.alive is True
        error = ex.value
        assert error.code == 5
        assert error.key == "RAISE_EXCEPTION"
        assert error.msg_number == "000"

    def test_RFC_RAISE_ERROR_AbapRuntimeError_E3(self):
        # '3_E': 'ABAPRuntimeError-3-COMPUTE_INT_ZERODIVIDE-Division by 0 (type I)-True''] ==
        # cf. ExceptionTest.c (l. 164ff)
        with pytest.raises(ABAPRuntimeError) as ex:
            self.conn.call("RFC_RAISE_ERROR", METHOD="3", MESSAGETYPE="E")
        assert self.conn.alive is True
        error = ex.value
        assert error.code == 3
        assert error.key == "COMPUTE_INT_ZERODIVIDE"

    def test_RFC_RAISE_ERROR_AbapRuntimeError_A(self):
        # cf. ExceptionTest.c (l. 112ff)
        with pytest.raises(ABAPRuntimeError) as ex:
            self.conn.call("RFC_RAISE_ERROR", MESSAGETYPE="A")
        assert self.conn.alive is True
        error = ex.value
        assert error.code == 4
        assert error.msg_class == "SR"
        assert error.msg_type == "A"
        assert error.msg_number == "006"
        assert error.msg_v1 == "Method = 0"

    def test_RFC_RAISE_ERROR_AbapRuntimeError_X(self):
        # cf. ExceptionTest.c (l. 137ff)
        with pytest.raises(ABAPRuntimeError) as ex:
            self.conn.call("RFC_RAISE_ERROR", MESSAGETYPE="X")
        assert self.conn.alive is True
        error = ex.value
        assert error.code == 4
        assert error.key == "MESSAGE_TYPE_X"
        assert error.msg_class == "00"
        assert error.msg_type == "X"
        assert error.msg_number == "341"
        assert error.msg_v1 == "MESSAGE_TYPE_X"

    def test_RFC_RAISE_ERROR_AbapRuntimeError_E36(self):
        # '36_E': 'ABAPRuntimeError-4-Division by 0 (type I)-Division by 0 (type I)-True''] ==
        with pytest.raises(ABAPRuntimeError) as ex:
            self.conn.call("RFC_RAISE_ERROR", METHOD="36", MESSAGETYPE="E")
        assert self.conn.alive is True
        error = ex.value
        assert error.code == 4
        assert "Division by 0" in str(error.message)

    def test_RFC_RAISE_ERROR_AbapRuntimeError_E51(self):
        # '51_E': 'ABAPRuntimeError-3-BLOCKED_COMMIT-A database commit was blocked by the application.-True''] ==
        with pytest.raises(ABAPRuntimeError) as ex:
            self.conn.call("RFC_RAISE_ERROR", METHOD="51", MESSAGETYPE="E")
        assert self.conn.alive is True
        error = ex.value
        assert error.code == 3
        assert error.key == "BLOCKED_COMMIT"

    def test_pyrfc_exc_string(self):
        with pytest.raises(ABAPApplicationError)as ex:
            self.conn.call("RFC_READ_TABLE", QUERY_TABLE="T008X", DELIMITER=".")
        error = ex.value
        assert error.code == 5
        assert error.key == "TABLE_NOT_AVAILABLE"
        assert error.message == "ID:SV Type:E Number:029 T008X"
        assert error.msg_type == "E"
        assert error.msg_number == "029"
        assert error.msg_v1 == "T008X"
        assert str(error) == "5 (rc=5): key=TABLE_NOT_AVAILABLE, message=ID:SV Type:E Number:029 T008X [MSG: class=SV, type=E, number=029, v1-4:=T008X;;;]"

    # def test_RFC_RAISE_ERROR_ExternalRuntimeError(self):
    #     # Comment: cf. result_print of the error_test.py
    #     # '11_E': 'ExternalRuntimeError-17-RFC_NOT_FOUND-Function RFCPING not found-True',
    #     try:
    #         self.conn.call("RFC_RAISE_ERROR", METHOD="17", MESSAGETYPE="E")
    #     with pytest.raises(ExternalRuntimeError) as ex:
    #         assert True
    #         error = ex.value
    #         assert error.code == 17
    #         assert error.key =="RFC_NOT_FOUND"

    # def test_RFC_RAISE_ERROR_CommunicationError(self):
    #     # Comment: cf. result_print of the error_test.py
    #     # '32_E': 'CommunicationError-1-RFC_COMMUNICATION_FAILURE-connection closed without message
    #     # (CM_NO_DATA_RECEIVED)-True',
    #     try:
    #         self.conn.call("RFC_RAISE_ERROR", METHOD="32", MESSAGETYPE="E")

    #     with pytest.raises(CommunicationError) as ex:
    #         error = ex.value
    #         assert error.code == 1
    #         assert error.key =="RFC_COMMUNICATION_FAILURE"

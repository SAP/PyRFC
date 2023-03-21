#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

import pytest
from pyrfc import (
    Connection,
    RFCError,
    LogonError,
    ABAPApplicationError,
    ExternalRuntimeError,
)

from tests.config import PARAMS as params


class TestErrors:
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

    # todo: test correct status after error -> or to the error tests?
    def test_incomplete_params(self):
        incomplete_params = params.copy()
        for p in ["ashost", "gwhost", "mshost"]:
            if p in incomplete_params:
                del incomplete_params[p]
        with pytest.raises(RFCError) as ex:
            Connection(**incomplete_params)
        error = ex.value
        assert error.code == 20
        assert error.key == "RFC_INVALID_PARAMETER"
        assert error.message in [
            "Parameter ASHOST, GWHOST, MSHOST or SERVER_PORT is missing.",
            "Parameter ASHOST, GWHOST, MSHOST or PORT is missing.",
            "Parameter ASHOST, GWHOST or MSHOST is missing.",
        ]

    def test_denied_users(self):
        denied_params = params.copy()
        denied_params["user"] = "BLAFASEL"
        with pytest.raises(LogonError) as ex:
            Connection(**denied_params)
        error = ex.value
        assert error.code == 2
        assert error.key == "RFC_LOGON_FAILURE"
        assert error.message == "Name or password is incorrect (repeat logon)"

    def test_call_without_RFM_name(self):
        with pytest.raises(Exception) as ex:
            self.conn.call()
        error = ex.value
        assert isinstance(error, TypeError) is True
        assert error.args[0] == "call() takes at least 1 positional argument (0 given)"

    def test_call_non_existing_RFM(self):
        with pytest.raises(ABAPApplicationError) as ex:
            self.conn.call("undefined")
        error = ex.value
        assert error.code == 5
        assert error.key == "FU_NOT_FOUND"
        assert error.message == "ID:FL Type:E Number:046 undefined"

    def test_call_non_string_RFM_name(self):
        with pytest.raises(RFCError) as ex:
            self.conn.call(1)
        error = ex.value
        assert error.args == (
            "Remote function module name must be unicode string, received:",
            1,
            int,
        )

    def test_call_non_existing_RFM_parameter(self):
        with pytest.raises(ExternalRuntimeError) as ex:
            self.conn.call("STFC_CONNECTION", undefined=0)
        error = ex.value
        assert error.code == 20
        assert error.key == "RFC_INVALID_PARAMETER"
        assert error.message == "field 'undefined' not found"

    def test_non_existing_field_structure(self):
        IMPORTSTRUCT = {"XRFCCHAR1": "A", "RFCCHAR2": "BC", "RFCCHAR4": "DEFG"}
        with pytest.raises(ExternalRuntimeError) as ex:
            self.conn.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)
        error = ex.value
        assert error.code == 20
        assert error.key == "RFC_INVALID_PARAMETER"
        assert error.message == "field 'XRFCCHAR1' not found"

    def test_non_existing_field_table(self):
        IMPORTSTRUCT = {"XRFCCHAR1": "A", "RFCCHAR2": "BC", "RFCCHAR4": "DEFG"}
        with pytest.raises(ExternalRuntimeError) as ex:
            self.conn.call("STFC_STRUCTURE", RFCTABLE=[IMPORTSTRUCT])
        error = ex.value
        assert error.code == 20
        assert error.key == "RFC_INVALID_PARAMETER"
        assert error.message == "field 'XRFCCHAR1' not found"

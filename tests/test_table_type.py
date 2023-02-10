#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

from pyrfc import Connection

from tests.config import PARAMS as params


class TestTT:
    """
    This test cases cover table types of variable and structure types
    """

    def setup_method(self):
        self.conn = Connection(**params)
        assert self.conn.alive

    def teardown_method(self):
        self.conn.close()
        assert not self.conn.alive

    def test_TABLE_TYPE(self):
        result = self.conn.call(
            "/COE/RBP_PAM_SERVICE_ORD_CHANG",
            IV_ORDERID="4711",
            IT_NOTICE_NOTIFICATION=[{"": "ABCD"}, {"": "XYZ"}],
        )
        assert len(result["ET_RETURN"]) > 0
        erl = result["ET_RETURN"][0]
        assert erl["TYPE"] == "E"
        assert erl["ID"] == "IWO_BAPI"
        assert erl["NUMBER"] == "121"
        assert erl["MESSAGE_V1"] == "4711"

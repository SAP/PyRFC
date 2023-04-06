#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

import datetime
import pyrfc

from tests.config import (
    CONFIG_SECTIONS as config_sections,
)


class TestConnection:

    def test_config_rstrip_false(self):
        conn = pyrfc.Connection(config={"rstrip": False}, **config_sections["coevi51"])

        # Test with rstrip=False (input length=255 char)
        hello = "Hällo SAP!" + " " * 245
        result = conn.call("STFC_CONNECTION", REQUTEXT=hello)
        assert result["ECHOTEXT"] == hello

        # Test with rstrip=False (input length=10 char)
        result = conn.call("STFC_CONNECTION", REQUTEXT=hello.rstrip())
        assert result["ECHOTEXT"] == hello
        conn.close()

    def test_config_rstrip_true(self):
        conn = pyrfc.Connection(**config_sections["coevi51"])

        # Test with rstrip=True (input length=255 char)
        hello = "Hällo SAP!" + " " * 245
        result = conn.call("STFC_CONNECTION", REQUTEXT=hello)
        assert result["ECHOTEXT"] == hello.rstrip()

        # Test with rstrip=True (input length=10 char)
        result = conn.call("STFC_CONNECTION", REQUTEXT=hello.rstrip())
        assert result["ECHOTEXT"] == hello.rstrip()
        conn.close()

    def test_config_dtime_true(self):
        conn = pyrfc.Connection(config={"dtime": True}, **config_sections["coevi51"])
        # dates as datetime objects
        dates = conn.call("BAPI_USER_GET_DETAIL", USERNAME="demo")["LASTMODIFIED"]
        assert type(dates["MODDATE"]) is datetime.date
        assert type(dates["MODTIME"]) is datetime.time
        conn.close()

    def test_config_dtime_false(self):
        conn = pyrfc.Connection(**config_sections["coevi51"])
        # dates as strings
        dates = conn.call("BAPI_USER_GET_DETAIL", USERNAME="demo")["LASTMODIFIED"]
        assert type(dates["MODDATE"]) is not datetime.date
        assert type(dates["MODDATE"]) is not datetime.time
        conn.close()

    def test_config_return_import_params_false(self):
        # no import params return
        conn = pyrfc.Connection(**config_sections["coevi51"])
        hello = "Hällo SAP!"
        result = conn.call("STFC_CONNECTION", REQUTEXT=hello)
        assert "REQTEXT" not in result
        conn.close()

    def test_config_return_import_params_true(self):
        # return import params
        conn = pyrfc.Connection(config={"return_import_params": True}, **config_sections["coevi51"])
        result = conn.call("STFC_CONNECTION", REQUTEXT="hello")
        assert "REQUTEXT" in result
        conn.close()


"""
    def test_config_parameter(self):
        conn = pyrfc.Connection(config={"dtime": True}, **config_sections["coevi51"])
        # dtime test
        dates = conn.call("BAPI_USER_GET_DETAIL", USERNAME="demo")["LASTMODIFIED"]
        assert type(dates["MODDATE"]) is datetime.date
        assert type(dates["MODTIME"]) is datetime.time
        conn.close()
        conn = pyrfc.Connection(**config_sections["coevi51"])
        dates = conn.call("BAPI_USER_GET_DETAIL", USERNAME="demo")["LASTMODIFIED"]
        assert type(dates["MODDATE"]) is not datetime.date
        assert type(dates["MODDATE"]) is not datetime.time
        del conn
        # no import params return
        hello = "Hällo SAP!"
        result = self.conn.call("STFC_CONNECTION", REQUTEXT=hello)
        assert "REQTEXT" not in result
        # return import params
        conn = pyrfc.Connection(config={"return_import_params": True}, **config_sections["coevi51"])
        result = conn.call("STFC_CONNECTION", REQUTEXT=hello.rstrip())
        assert hello.rstrip() == result["REQUTEXT"]
        conn.close()
"""

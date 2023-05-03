#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import datetime
import socket
import sys
import pytest
from contextlib import suppress

with suppress(ModuleNotFoundError):
    import tomllib

from pyrfc import (
    Connection,
    RFCError,
    ExternalRuntimeError,
    __version__,
)

from tests.config import (
    PARAMS as params,
    PARAMSDEST as paramsdest,
    CONFIG_SECTIONS as config_sections,
    UNICODETEST,
    latest_python_version,
)


class TestConnection:
    def setup_method(self):
        self.conn = Connection(**paramsdest)
        assert self.conn.alive

    def teardown_method(self):
        self.conn.close()
        assert not self.conn.alive

    def test_sdk_version_and_options_getters(self):
        version = self.conn.version
        assert "major" in version
        assert "minor" in version
        assert "patchLevel" in version
        assert all(
            attr in self.conn.options
            for attr in (
                "dtime",
                "return_import_params",
                "rstrip",
            )
        )

    @pytest.mark.skipif(
        "tomllib" not in sys.modules or sys.version_info < latest_python_version,
        reason="pyrfc version check on latest python only",
    )
    def test_pyrfc_version(self):
        with open("pyproject.toml", "rb") as file:
            pyproject = tomllib.load(file)
        package_name = pyproject["project"]["name"]
        version = pyproject["project"]["version"]
        assert package_name == "pyrfc"
        assert version == __version__

    def test_connection_info(self):
        connection_info = self.conn.get_connection_attributes()
        info_keys = (
            "dest",
            "host",
            "partnerHost",
            "sysNumber",
            "sysId",
            "client",
            "user",
            "language",
            "trace",
            "isoLanguage",
            "codepage",
            "partnerCodepage",
            "rfcRole",
            "type",
            "partnerType",
            "rel",
            "partnerRel",
            "kernelRel",
            "cpicConvId",
            "progName",
            "partnerBytesPerChar",
            "partnerIP",
            "partnerIPv6"
            # 'reserved'
        )
        assert all(attr in connection_info for attr in info_keys)

    def test_connection_info_attributes(self):
        attributes = self.conn.get_connection_attributes()
        assert attributes["client"] == str(params["client"])
        assert attributes["host"] == str(socket.gethostname())
        assert attributes["isoLanguage"] == str(params["lang"].upper())
        # Only valid for direct logon systems:
        # self.assertEqual(attributes['sysNumber'], str(params['sysnr']))
        assert attributes["user"] == str(params["user"].upper())
        assert attributes["rfcRole"] == "C"

    def test_connection_info_disconnected(self):
        self.conn.close()
        assert not self.conn.alive
        connection_info = self.conn.get_connection_attributes()
        assert connection_info == {}

    def test_reopen(self):
        assert self.conn.alive
        self.conn.reopen()
        assert self.conn.alive
        self.conn.close()
        assert not self.conn.alive
        self.conn.reopen()
        assert self.conn.alive

    def test_call_over_closed_connection(self):
        conn = Connection(
            config={"rstrip": False},
            **config_sections["coevi51"],
        )
        conn.close()
        assert conn.alive is False
        hello = "Hällo SAP!"
        with pytest.raises(RFCError) as ex:
            conn.call(
                "STFC_CONNECTION",
                REQUTEXT=hello,
            )
        error = ex.value
        assert (
            error.args[0] == "Remote function module 'STFC_CONNECTION' invocation "
            "rejected because the connection is closed"
        )

    def test_ping(self):
        assert self.conn.alive
        self.conn.ping()
        self.conn.close()
        with pytest.raises(ExternalRuntimeError) as ex:
            self.conn.ping()
        error = ex.value
        assert error.code == 13
        assert error.key == "RFC_INVALID_HANDLE"
        assert error.message in [
            "An invalid handle 'RFC_CONNECTION_HANDLE' was passed to the API call",
            "An invalid handle was passed to the API call",
        ]

    def test_RFM_name_string(self):
        res = self.conn.call(
            "STFC_CONNECTION",
            REQUTEXT=UNICODETEST,
        )
        assert res["ECHOTEXT"] == UNICODETEST

    def test_RFM_name_unicode(self):
        res = self.conn.call(
            "STFC_CONNECTION",
            REQUTEXT=UNICODETEST,
        )
        assert res["ECHOTEXT"] == UNICODETEST

    def test_RFM_name_invalid_type(self):
        with pytest.raises(Exception) as ex:
            self.conn.call(123)
        error = ex.value
        assert error.args == (
            "Remote function module name must be unicode string, received:",
            123,
            int,
        )

    def test_STFC_returns_structure_and_table(self):
        IMPORTSTRUCT = {
            "RFCFLOAT": 1.23456789,
            "RFCCHAR1": "A",
            "RFCCHAR2": "BC",
            "RFCCHAR4": "DEFG",
            "RFCINT1": 1,
            "RFCINT2": 2,
            "RFCINT4": 345,
            "RFCHEX3": bytes(b"\x01\x02\x03"),
            "RFCTIME": "121120",
            "RFCDATE": "20140101",
            "RFCDATA1": "1DATA1",
            "RFCDATA2": "DATA222",
        }
        INPUTROWS = 10
        IMPORTTABLE = []
        for idx in range(INPUTROWS):
            row = IMPORTSTRUCT
            row["RFCINT1"] = idx
            IMPORTTABLE.append(row)
        res = self.conn.call(
            "STFC_STRUCTURE",
            IMPORTSTRUCT=IMPORTSTRUCT,
            RFCTABLE=IMPORTTABLE,
        )
        # ECHOSTRUCT match IMPORTSTRUCT
        for attr in IMPORTSTRUCT:
            assert res["ECHOSTRUCT"][attr] == IMPORTSTRUCT[attr]

        # check if row added
        assert len(res["RFCTABLE"]) == INPUTROWS + 1

        # output table match import table
        for idx in range(INPUTROWS):
            row_in = IMPORTTABLE[idx]
            row_out = res["RFCTABLE"][idx]
            assert row_in == row_out

        # added row match incremented IMPORTSTRUCT
        added_row = res["RFCTABLE"][INPUTROWS]
        assert added_row["RFCFLOAT"] == IMPORTSTRUCT["RFCFLOAT"] + 1
        assert added_row["RFCINT1"] == IMPORTSTRUCT["RFCINT1"] + 1
        assert added_row["RFCINT2"] == IMPORTSTRUCT["RFCINT2"] + 1
        assert added_row["RFCINT4"] == IMPORTSTRUCT["RFCINT4"] + 1

    def test_STFC_STRUCTURE(self):
        # STFC_STRUCTURE Inhomogene Struktur
        imp = {
            "RFCFLOAT": 1.23456789,
            "RFCINT2": 0x7FFE,
            "RFCINT1": 0x7F,
            "RFCCHAR4": "bcde",
            "RFCINT4": 0x7FFFFFFE,
            "RFCHEX3": "fgh".encode("utf-8"),
            "RFCCHAR1": "a",
            "RFCCHAR2": "ij",
            "RFCTIME": "123456",  # datetime.time(12,34,56),
            "RFCDATE": "20161231",  # datetime.date(2011,10,17),
            "RFCDATA1": "k" * 50,
            "RFCDATA2": "l" * 50,
        }
        out = {
            "RFCFLOAT": imp["RFCFLOAT"] + 1,  # type: ignore
            "RFCINT2": imp["RFCINT2"] + 1,  # type: ignore
            "RFCINT1": imp["RFCINT1"] + 1,  # type: ignore
            "RFCINT4": imp["RFCINT4"] + 1,  # type: ignore
            "RFCHEX3": b"\xf1\xf2\xf3",
            "RFCCHAR1": "X",
            "RFCCHAR2": "YZ",
            "RFCDATE": str(datetime.date.today()).replace(
                "-",
                "",
            ),
            "RFCDATA1": "k" * 50,
            "RFCDATA2": "l" * 50,
        }
        table = []
        xtable = []
        records = [
            "1111",
            "2222",
            "3333",
            "4444",
            "5555",
        ]
        for rid in records:
            imp["RFCCHAR4"] = rid
            table.append(imp)
            xtable.append(imp)
        # print 'table len', len(table), len(xtable)
        res = self.conn.call(
            "STFC_STRUCTURE",
            IMPORTSTRUCT=imp,
            RFCTABLE=xtable,
        )
        # print 'table len', len(table), len(xtable)
        assert res["RESPTEXT"].startswith("SAP")
        # assert res['ECHOSTRUCT'] == imp
        assert len(res["RFCTABLE"]) == 1 + len(table)
        for idx in res["ECHOSTRUCT"]:
            assert res["ECHOSTRUCT"][idx] == imp[idx]
        for idx in res["RFCTABLE"][5]:
            # dont compare variable system id and server time
            if idx not in [
                "RFCCHAR4",
                "RFCTIME",
            ]:
                assert res["RFCTABLE"][5][idx] == out[idx]

    def test_STFC_CHANGING(self):
        # STFC_CHANGING example with CHANGING parameters
        start_value = 33
        counter = 88
        res = self.conn.call(
            "STFC_CHANGING",
            START_VALUE=start_value,
            COUNTER=counter,
        )
        assert res["COUNTER"] == counter + 1
        assert res["RESULT"] == start_value + counter


"""
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
"""

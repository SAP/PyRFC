# -*- coding: utf-8 -*-

# Copyright 2014 SAP AG.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http: //www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
# either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import os
import sys
import datetime
import unittest
from decimal import Decimal

import pytest
from pyrfc import *

from tests.config import (
    CONNECTION_INFO,
    RFC_MATH,
    ABAP_to_python_date,
    ABAP_to_python_time,
    python_to_ABAP_date,
    python_to_ABAP_time,
    UNICODETEST,
)

client = Connection(**CONNECTION_INFO)


def test_basic_datatypes():
    INPUTS = [
        dict(
            # Float
            ZFLTP=0.123456789,
            # Decimal
            ZDEC=12345.67,
            # Currency, Quantity
            ZCURR=1234.56,
            ZQUAN=12.3456,
            ZQUAN_SIGN=-12.345,
        ),
        dict(
            # Float
            ZFLTP=Decimal("0.123456789"),
            # Decimal
            ZDEC=Decimal("12345.67"),
            # Currency, Quantity
            ZCURR=Decimal("1234.56"),
            ZQUAN=Decimal("12.3456"),
            ZQUAN_SIGN=Decimal("-12.345"),
        ),
        dict(
            # Float
            ZFLTP="0.123456789",
            # Decimal
            ZDEC="12345.67",
            # Currency, Quantity
            ZCURR="1234.56",
            ZQUAN="12.3456",
            ZQUAN_SIGN="-12.345",
        ),
    ]

    for is_input in INPUTS:
        result = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=is_input)["ES_OUTPUT"]
        for k in is_input:
            in_value = is_input[k]
            out_value = result[k]
            if k == "ZFLTP":
                assert type(out_value) is float
            else:
                assert type(out_value) is Decimal
            if type(in_value) != type(out_value):
                assert str(in_value) == str(out_value)
            else:
                assert in_value == out_value


def test_date_output():
    lm = client.call("BAPI_USER_GET_DETAIL", USERNAME="demo")["LASTMODIFIED"]
    assert len(lm["MODDATE"]) > 0
    assert len(lm["MODTIME"]) > 0


def test_min_max_positive():
    IS_INPUT = {
        # Float
        "ZFLTP_MIN": RFC_MATH["FLOAT"]["POS"]["MIN"],
        "ZFLTP_MAX": RFC_MATH["FLOAT"]["POS"]["MAX"],
        # Decimal
        "ZDECF16_MIN": RFC_MATH["DECF16"]["POS"]["MIN"],
        "ZDECF16_MAX": RFC_MATH["DECF16"]["POS"]["MAX"],
        "ZDECF34_MIN": RFC_MATH["DECF34"]["POS"]["MIN"],
        "ZDECF34_MAX": RFC_MATH["DECF34"]["POS"]["MAX"],
    }

    output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
        "ES_OUTPUT"
    ]

    assert type(output["ZFLTP_MIN"]) is float
    assert type(output["ZFLTP_MAX"]) is float
    assert type(output["ZDECF16_MIN"]) is Decimal
    assert type(output["ZDECF16_MAX"]) is Decimal
    assert type(output["ZDECF34_MAX"]) is Decimal
    assert type(output["ZDECF16_MIN"]) is Decimal

    assert float(IS_INPUT["ZFLTP_MIN"]) == output["ZFLTP_MIN"]
    assert float(IS_INPUT["ZFLTP_MAX"]) == output["ZFLTP_MAX"]
    assert Decimal(IS_INPUT["ZDECF16_MIN"]) == output["ZDECF16_MIN"]
    assert Decimal(IS_INPUT["ZDECF16_MAX"]) == output["ZDECF16_MAX"]
    assert Decimal(IS_INPUT["ZDECF16_MIN"]) == output["ZDECF16_MIN"]
    assert Decimal(IS_INPUT["ZDECF34_MAX"]) == output["ZDECF34_MAX"]


def test_min_max_negative():
    IS_INPUT = {
        # Float
        "ZFLTP_MIN": RFC_MATH["FLOAT"]["NEG"]["MIN"],
        "ZFLTP_MAX": RFC_MATH["FLOAT"]["NEG"]["MAX"],
        # Decimal
        "ZDECF16_MIN": RFC_MATH["DECF16"]["NEG"]["MIN"],
        "ZDECF16_MAX": RFC_MATH["DECF16"]["NEG"]["MAX"],
        "ZDECF34_MIN": RFC_MATH["DECF34"]["NEG"]["MIN"],
        "ZDECF34_MAX": RFC_MATH["DECF34"]["NEG"]["MAX"],
    }

    output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
        "ES_OUTPUT"
    ]

    assert type(output["ZFLTP_MIN"]) is float
    assert type(output["ZFLTP_MAX"]) is float
    assert type(output["ZDECF16_MIN"]) is Decimal
    assert type(output["ZDECF16_MAX"]) is Decimal
    assert type(output["ZDECF16_MIN"]) is Decimal
    assert type(output["ZDECF34_MAX"]) is Decimal

    assert float(IS_INPUT["ZFLTP_MIN"]) == output["ZFLTP_MIN"]
    assert float(IS_INPUT["ZFLTP_MAX"]) == output["ZFLTP_MAX"]
    assert Decimal(IS_INPUT["ZDECF16_MIN"]) == output["ZDECF16_MIN"]
    assert Decimal(IS_INPUT["ZDECF16_MAX"]) == output["ZDECF16_MAX"]
    assert Decimal(IS_INPUT["ZDECF16_MIN"]) == output["ZDECF16_MIN"]
    assert Decimal(IS_INPUT["ZDECF34_MAX"]) == output["ZDECF34_MAX"]


def test_bcd_floats_accept_floats():
    IS_INPUT = {
        # Float
        "ZFLTP": 0.123456789,
        # Decimal
        "ZDEC": 12345.67,
        "ZDECF16_MIN": 12345.67,
        "ZDECF34_MIN": 12345.67,
        # Currency, Quantity
        "ZCURR": 1234.56,
        "ZQUAN": 12.3456,
        "ZQUAN_SIGN": -12.345,
    }

    output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
        "ES_OUTPUT"
    ]
    assert type(output["ZFLTP"]) is float
    assert IS_INPUT["ZFLTP"] == output["ZFLTP"]

    assert type(output["ZDEC"]) is Decimal
    assert str(IS_INPUT["ZDEC"]) == str(output["ZDEC"])
    assert IS_INPUT["ZDEC"] == float(output["ZDEC"])

    assert type(output["ZDECF16_MIN"]) is Decimal
    assert str(IS_INPUT["ZDECF16_MIN"]) == str(output["ZDECF16_MIN"])
    assert IS_INPUT["ZDECF16_MIN"] == float(output["ZDECF16_MIN"])

    assert type(output["ZDECF34_MIN"]) is Decimal
    assert str(IS_INPUT["ZDECF34_MIN"]) == str(output["ZDECF34_MIN"])
    assert IS_INPUT["ZDECF34_MIN"] == float(output["ZDECF34_MIN"])

    assert type(output["ZCURR"]) is Decimal
    assert str(IS_INPUT["ZCURR"]) == str(output["ZCURR"])
    assert IS_INPUT["ZCURR"] == float(output["ZCURR"])

    assert type(output["ZQUAN"]) is Decimal
    assert str(IS_INPUT["ZQUAN"]) == str(output["ZQUAN"])
    assert IS_INPUT["ZQUAN"] == float(output["ZQUAN"])

    assert type(output["ZQUAN_SIGN"]) is Decimal
    assert str(IS_INPUT["ZQUAN_SIGN"]) == str(output["ZQUAN_SIGN"])
    assert IS_INPUT["ZQUAN_SIGN"] == float(output["ZQUAN_SIGN"])


def test_bcd_floats_accept_strings():
    IS_INPUT = {
        # Float
        "ZFLTP": "0.123456789",
        # Decimal
        "ZDEC": "12345.67",
        "ZDECF16_MIN": "12345.67",
        "ZDECF34_MIN": "12345.67",
        # Currency, Quantity
        "ZCURR": "1234.56",
        "ZQUAN": "12.3456",
        "ZQUAN_SIGN": "-12.345",
    }

    output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
        "ES_OUTPUT"
    ]
    assert type(output["ZFLTP"]) is float
    assert float(IS_INPUT["ZFLTP"]) == output["ZFLTP"]

    assert type(output["ZDEC"]) is Decimal
    assert IS_INPUT["ZDEC"] == str(output["ZDEC"])

    assert type(output["ZDECF16_MIN"]) is Decimal
    assert IS_INPUT["ZDECF16_MIN"] == str(output["ZDECF16_MIN"])

    assert type(output["ZDECF34_MIN"]) is Decimal
    assert IS_INPUT["ZDECF34_MIN"] == str(output["ZDECF34_MIN"])

    assert type(output["ZCURR"]) is Decimal
    assert IS_INPUT["ZCURR"] == str(output["ZCURR"])

    assert type(output["ZQUAN"]) is Decimal
    assert IS_INPUT["ZQUAN"] == str(output["ZQUAN"])

    assert type(output["ZQUAN_SIGN"]) is Decimal
    assert IS_INPUT["ZQUAN_SIGN"] == str(output["ZQUAN_SIGN"])


def test_bcd_floats_accept_decimals():
    IS_INPUT = {
        # Float
        "ZFLTP": Decimal("0.123456789"),
        # Decimal
        "ZDEC": Decimal("12345.67"),
        "ZDECF16_MIN": Decimal("12345.67"),
        "ZDECF34_MIN": Decimal("12345.67"),
        # Currency, Quantity
        "ZCURR": Decimal("1234.56"),
        "ZQUAN": Decimal("12.3456"),
        "ZQUAN_SIGN": Decimal("-12.345"),
    }

    output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
        "ES_OUTPUT"
    ]
    assert type(output["ZFLTP"]) is float
    assert IS_INPUT["ZFLTP"] == Decimal(str(output["ZFLTP"]))

    assert type(output["ZDEC"]) is Decimal
    assert IS_INPUT["ZDEC"] == Decimal(str(output["ZDEC"]))

    assert type(output["ZDECF16_MIN"]) is Decimal
    assert IS_INPUT["ZDECF16_MIN"] == Decimal(str(output["ZDECF16_MIN"]))

    assert type(output["ZDECF34_MIN"]) is Decimal
    assert IS_INPUT["ZDECF34_MIN"] == Decimal(str(output["ZDECF34_MIN"]))

    assert type(output["ZCURR"]) is Decimal
    assert IS_INPUT["ZCURR"] == Decimal(str(output["ZCURR"]))

    assert type(output["ZQUAN"]) is Decimal
    assert IS_INPUT["ZQUAN"] == Decimal(str(output["ZQUAN"]))

    assert type(output["ZQUAN_SIGN"]) is Decimal
    assert IS_INPUT["ZQUAN_SIGN"] == Decimal(str(output["ZQUAN_SIGN"]))


def test_raw_types_accept_bytes():
    str_unicode = u"四周远处都"
    if sys.version > "3.0":
        ZRAW = bytes(str_unicode, encoding="utf-8")  # or str_unicode.encode("utf-8")
    else:
        # todo Python 2
        ZRAW = str_unicode.encode("utf-8")
    IS_INPUT = {"ZRAW": ZRAW, "ZRAWSTRING": ZRAW}
    output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
        "ES_OUTPUT"
    ]

    assert output["ZRAW"] == ZRAW
    assert output["ZRAWSTRING"] == ZRAW
    assert type(output["ZRAW"]) is bytes
    assert type(output["ZRAWSTRING"]) is bytes


def test_raw_types_accept_bytearray():
    str_unicode = u"四周远处都"
    if sys.version > "3.0":
        ZRAW = bytearray(
            str_unicode, encoding="utf-8"
        )  # or str_unicode.encode("utf-8")
    else:
        # todo Python 2
        ZRAW = str_unicode.encode("utf-8")
    IS_INPUT = {"ZRAW": ZRAW, "ZRAWSTRING": ZRAW}
    output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
        "ES_OUTPUT"
    ]

    assert output["ZRAW"] == ZRAW
    assert output["ZRAWSTRING"] == ZRAW
    assert type(output["ZRAW"]) is bytes
    assert type(output["ZRAWSTRING"]) is bytes


def test_date_time():
    DATETIME_TEST = [
        {"RFCDATE": "20161231", "RFCTIME": "123456"},  # good
        {"RFCDATE": "2016123", "RFCTIME": "123456"},  # shorter date
        {"RFCDATE": "201612311", "RFCTIME": "123456"},  # longer date
        {"RFCDATE": "20161232", "RFCTIME": "123456"},  # out of range date
        {"RFCDATE": 20161231, "RFCTIME": "123456"},  # wrong date type
        {"RFCDATE": "20161231", "RFCTIME": "12345"},  # shorter time
        {"RFCDATE": "20161231", "RFCTIME": "1234566"},  # longer time
        {"RFCDATE": "20161231", "RFCTIME": "123466"},  # out of range time
        {"RFCDATE": "20161231", "RFCTIME": 123456},  # wrong time type
    ]
    counter = 0
    for dt in DATETIME_TEST:
        counter += 1
        try:
            result = client.call("STFC_STRUCTURE", IMPORTSTRUCT=dt)["ECHOSTRUCT"]
            assert dt["RFCDATE"] == result["RFCDATE"]
            assert dt["RFCTIME"] == result["RFCTIME"]
            assert counter == 1
        except Exception as e:
            assert type(e) is TypeError
            if counter < 6:
                assert e.args == (
                    "a date value required, received",
                    dt["RFCDATE"],
                    "RFCDATE",
                    "IMPORTSTRUCT",
                )
            else:
                assert e.args == (
                    "a time value required, received",
                    dt["RFCTIME"],
                    "RFCTIME",
                    "IMPORTSTRUCT",
                )


def test_date_accepts_string():
    TEST_DATE = u"20180625"

    IMPORTSTRUCT = {"RFCDATE": TEST_DATE}
    IMPORTTABLE = [IMPORTSTRUCT]
    output = client.call(
        "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=IMPORTTABLE
    )
    if sys.version > "3.0":
        assert type(output["ECHOSTRUCT"]["RFCDATE"]) is str
        assert type(output["RFCTABLE"][0]["RFCDATE"]) is str
    else:
        assert type(output["ECHOSTRUCT"]["RFCDATE"]) is unicode
        assert type(output["RFCTABLE"][0]["RFCDATE"]) is unicode
    assert output["ECHOSTRUCT"]["RFCDATE"] == TEST_DATE
    assert output["RFCTABLE"][0]["RFCDATE"] == TEST_DATE


def test_date_accepts_date():
    TEST_DATE = ABAP_to_python_date("20180625")

    IMPORTSTRUCT = {"RFCDATE": TEST_DATE}
    IMPORTTABLE = [IMPORTSTRUCT]
    output = client.call(
        "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=IMPORTTABLE
    )
    if sys.version > "3.0":
        assert type(output["ECHOSTRUCT"]["RFCDATE"]) is str
        assert type(output["RFCTABLE"][0]["RFCDATE"]) is str
    else:
        assert type(output["ECHOSTRUCT"]["RFCDATE"]) is unicode
        assert type(output["RFCTABLE"][0]["RFCDATE"]) is unicode
    assert output["ECHOSTRUCT"]["RFCDATE"] == python_to_ABAP_date(TEST_DATE)
    assert output["RFCTABLE"][0]["RFCDATE"] == python_to_ABAP_date(TEST_DATE)


def test_time_accepts_string():
    TEST_TIME = "123456"

    IMPORTSTRUCT = {"RFCTIME": TEST_TIME}
    IMPORTTABLE = [IMPORTSTRUCT]
    output = client.call(
        "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=IMPORTTABLE
    )
    if sys.version > "3.0":
        assert type(output["ECHOSTRUCT"]["RFCTIME"]) is str
        assert type(output["RFCTABLE"][0]["RFCTIME"]) is str
    else:
        assert type(output["ECHOSTRUCT"]["RFCTIME"]) is unicode
        assert type(output["RFCTABLE"][0]["RFCTIME"]) is unicode
    assert output["ECHOSTRUCT"]["RFCTIME"] == TEST_TIME
    assert output["RFCTABLE"][0]["RFCTIME"] == TEST_TIME


def test_time_accepts_time():
    TEST_TIME = ABAP_to_python_time("123456")

    IMPORTSTRUCT = {"RFCTIME": TEST_TIME}
    IMPORTTABLE = [IMPORTSTRUCT]
    output = client.call(
        "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=IMPORTTABLE
    )
    if sys.version > "3.0":
        assert type(output["ECHOSTRUCT"]["RFCTIME"]) is str
        assert type(output["RFCTABLE"][0]["RFCTIME"]) is str
    else:
        assert type(output["ECHOSTRUCT"]["RFCTIME"]) is unicode
        assert type(output["RFCTABLE"][0]["RFCTIME"]) is unicode
    assert output["ECHOSTRUCT"]["RFCTIME"] == python_to_ABAP_time(TEST_TIME)
    assert output["RFCTABLE"][0]["RFCTIME"] == python_to_ABAP_time(TEST_TIME)


def test_error_int_rejects_string():
    IMPORTSTRUCT = {"RFCINT1": "1"}
    RFCTABLE = [IMPORTSTRUCT]
    try:
        output = client.call(
            "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=RFCTABLE
        )
    except Exception as ex:
        assert type(ex) is TypeError
        if sys.version > "3.0":
            assert ex.args == (
                "an integer is required, received",
                "1",
                "RFCINT1",
                "IMPORTSTRUCT",
            )
        else:
            assert ex.args == (
                "an integer is required, received",
                "1",
                "RFCINT1",
                "RFCTABLE",
            )


def test_error_int_rejects_float():
    IMPORTSTRUCT = {"RFCINT1": 1.0}
    RFCTABLE = [IMPORTSTRUCT]
    try:
        output = client.call(
            "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=RFCTABLE
        )
    except Exception as ex:
        assert type(ex) is TypeError
        if sys.version > "3.0":
            assert ex.args == (
                "an integer is required, received",
                1.0,
                "RFCINT1",
                "IMPORTSTRUCT",
            )
        else:
            assert ex.args == (
                "an integer is required, received",
                1.0,
                "RFCINT1",
                "RFCTABLE",
            )


def test_error_string_rejects_int():
    IMPORTSTRUCT = {"RFCCHAR4": None}
    RFCTABLE = [IMPORTSTRUCT]
    try:
        output = client.call(
            "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=RFCTABLE
        )
    except Exception as ex:
        assert type(ex) is TypeError
        if sys.version > "3.0":
            assert ex.args == (
                "an string is required, received",
                None,
                "of type:",
                "<class 'NoneType'>",
                "RFCCHAR4",
                "IMPORTSTRUCT",
            )
        else:
            assert ex.args == (
                "an string is required, received",
                None,
                "of type:",
                "<type 'NoneType'>",
                "RFCCHAR4",
                "RFCTABLE",
            )


def test_float_rejects_not_a_number_string():
    IMPORTSTRUCT = {"RFCFLOAT": "A"}
    RFCTABLE = [IMPORTSTRUCT]
    try:
        output = client.call(
            "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=RFCTABLE
        )
    except Exception as ex:
        assert type(ex) is TypeError
        if sys.version > '3.0':
            assert ex.args == (
                "a decimal value is required, received",
                "A",
                "RFCFLOAT",
                "IMPORTSTRUCT",
            )
        else:
            assert ex.args == (
                "a decimal value is required, received",
                "A",
                "RFCFLOAT",
                "RFCTABLE",
            )



def test_bcd_rejects_not_a_number_string():

    try:
        IS_INPUT = {"ZDEC": "A"}
        output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
            "ES_OUTPUT"
        ]
    except Exception as ex:
        assert type(ex) is TypeError
        assert ex.args == (
            "a decimal value is required, received",
            "A",
            "ZDEC",
            "IS_INPUT",
        )


client.close()

if __name__ == "__main__":
    unittest.main()

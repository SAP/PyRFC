# -*- coding: utf-8 -*-

# Copyright 2014 SAP AG.
# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import sys
from decimal import Decimal
from locale import setlocale, localeconv, LC_ALL

from pyrfc import Connection, set_locale_radix, ExternalRuntimeError

from tests.config import (
    CONNECTION_INFO,
    RFC_MATH,
    ABAP_to_python_date,
    ABAP_to_python_time,
    python_to_ABAP_date,
    python_to_ABAP_time,
    BYTEARRAY_TEST,
    BYTES_TEST,
)

from tests.abap_system import connection_info

setlocale(LC_ALL)

client = Connection(**CONNECTION_INFO)


def get_locale_radix():
    return localeconv()["decimal_point"]


def test_structure_rejects_non_dict():
    with pytest.raises(TypeError) as ex:
        IMPORTSTRUCT = {"RFCINT1": "1"}
        client.call("STFC_STRUCTURE", IMPORTSTRUCT=[IMPORTSTRUCT])
    error = ex.value
    assert error.args[0] == "dictionary required for structure parameter, received"
    assert error.args[1] == "<class 'list'>"
    assert error.args[2] == "IMPORTSTRUCT"


def test_table_rejects_non_list():
    with pytest.raises(TypeError) as ex:
        IMPORTSTRUCT = {"RFCINT1": "1"}
        client.call("STFC_STRUCTURE", RFCTABLE=IMPORTSTRUCT)
    error = ex.value
    assert error.args[0] == "list required for table parameter, received"
    assert error.args[1] == "<class 'dict'>"
    assert error.args[2] == "RFCTABLE"


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


def test_string_unicode():
    hello = "Hällo SAP!"
    result = client.call("STFC_CONNECTION", REQUTEXT=hello)["ECHOTEXT"]
    assert result == hello

    hello = "01234" * 51
    result = client.call("STFC_CONNECTION", REQUTEXT=hello)["ECHOTEXT"]
    assert result == hello

    unicode_test = [
        "string",
        "四周远处都能望见",
        "\U0001F4AA",
        "\u0001\uf4aa",
        "a\xac\u1234\u20ac\U0001F4AA",
    ]

    for s in unicode_test:
        is_input = {"ZSHLP_MAT1": s}
        result = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=is_input)["ES_OUTPUT"]
        assert is_input["ZSHLP_MAT1"] == result["ZSHLP_MAT1"]


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


def test_bcd_floats_accept_strings_radix_comma():
    # locale.setlocale(locale.LC_ALL, "de_DE")
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
    # locale.setlocale(locale.LC_ALL, "")


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
    ZRAW = BYTES_TEST
    DIFF = b"\x00\x00\x00\x00"
    IS_INPUT = {"ZRAW": ZRAW, "ZRAWSTRING": ZRAW}
    output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
        "ES_OUTPUT"
    ]
    assert output["ZRAW"] == ZRAW + DIFF
    assert output["ZRAWSTRING"] == ZRAW
    assert type(output["ZRAW"]) is bytes
    assert type(output["ZRAWSTRING"]) is bytes


def test_raw_types_accept_bytearray():
    ZRAW = BYTEARRAY_TEST
    DIFF = b"\x00\x00\x00\x00"
    IS_INPUT = {"ZRAW": ZRAW, "ZRAWSTRING": ZRAW}
    output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
        "ES_OUTPUT"
    ]
    assert output["ZRAW"] == ZRAW + DIFF
    assert output["ZRAWSTRING"] == ZRAW
    assert type(output["ZRAW"]) is bytes
    assert type(output["ZRAWSTRING"]) is bytes


def test_date_time():
    DATETIME_TEST = [
        {"RFCDATE": "20161231", "RFCTIME": "123456"},  # good, correct date
        {"RFCDATE": "", "RFCTIME": "123456"},  # good, empty date
        {"RFCDATE": "        ", "RFCTIME": "123456"},  # good, space date
        {"RFCDATE": "20161231", "RFCTIME": ""},  # good, empty time
        {"RFCDATE": "20161231", "RFCTIME": "      "},  # good, space time
        {"RFCDATE": "20161231", "RFCTIME": "000000"},  # good, zero time
        {"RFCDATE": "2016123", "RFCTIME": "123456"},  # shorter date
        {"RFCDATE": " ", "RFCTIME": "123456"},  # shorter empty date
        {"RFCDATE": "201612311", "RFCTIME": "123456"},  # longer date
        {"RFCDATE": "         ", "RFCTIME": "123456"},  # longer empty date
        {"RFCDATE": "20161232", "RFCTIME": "123456"},  # out of range date
        {"RFCDATE": 20161231, "RFCTIME": "123456"},  # wrong date type
        {"RFCDATE": "20161231", "RFCTIME": "12345"},  # shorter time
        {"RFCDATE": "20161231", "RFCTIME": " "},  # shorter empty time
        {"RFCDATE": "20161231", "RFCTIME": "1234566"},  # longer time
        {"RFCDATE": "20161231", "RFCTIME": "       "},  # longer empty time
        {"RFCDATE": "20161231", "RFCTIME": "123466"},  # out of range time
        {"RFCDATE": "20161231", "RFCTIME": 123456},  # wrong time type
    ]
    counter = 0
    for dt in DATETIME_TEST:
        counter += 1
        if counter < 7:
            result = client.call("STFC_STRUCTURE", IMPORTSTRUCT=dt)["ECHOSTRUCT"]
            assert dt["RFCDATE"] == result["RFCDATE"]
            if dt["RFCTIME"] == "":
                assert "000000" == result["RFCTIME"]
            else:
                assert dt["RFCTIME"] == result["RFCTIME"]
        else:
            with pytest.raises(TypeError) as ex:
                client.call("STFC_STRUCTURE", IMPORTSTRUCT=dt)["ECHOSTRUCT"]
            error = ex.value
            if counter < 13:
                assert error.args[0] == "date value required, received"
                assert error.args[1] == dt["RFCDATE"]
                assert isinstance(dt["RFCDATE"], error.args[3])
                assert error.args[4] == "RFCDATE"
            else:
                assert error.args[0] == "time value required, received"
                assert error.args[1] == dt["RFCTIME"]
                assert isinstance(dt["RFCTIME"], error.args[3])
                assert error.args[4] == "RFCTIME"
            assert error.args[5] == "IMPORTSTRUCT"


def test_date_accepts_string():
    TEST_DATE = "20180625"
    IMPORTSTRUCT = {"RFCDATE": TEST_DATE}
    IMPORTTABLE = [IMPORTSTRUCT]
    output = client.call(
        "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=IMPORTTABLE
    )
    assert type(output["ECHOSTRUCT"]["RFCDATE"]) is str
    assert type(output["RFCTABLE"][0]["RFCDATE"]) is str
    assert output["ECHOSTRUCT"]["RFCDATE"] == TEST_DATE
    assert output["RFCTABLE"][0]["RFCDATE"] == TEST_DATE


def test_date_accepts_date():
    TEST_DATE = ABAP_to_python_date("20180625")
    IMPORTSTRUCT = {"RFCDATE": TEST_DATE}
    IMPORTTABLE = [IMPORTSTRUCT]
    output = client.call(
        "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=IMPORTTABLE
    )
    assert type(output["ECHOSTRUCT"]["RFCDATE"]) is str
    assert type(output["RFCTABLE"][0]["RFCDATE"]) is str
    assert output["ECHOSTRUCT"]["RFCDATE"] == python_to_ABAP_date(TEST_DATE)
    assert output["RFCTABLE"][0]["RFCDATE"] == python_to_ABAP_date(TEST_DATE)


def test_time_accepts_string():
    TEST_TIME = "123456"
    IMPORTSTRUCT = {"RFCTIME": TEST_TIME}
    IMPORTTABLE = [IMPORTSTRUCT]
    output = client.call(
        "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=IMPORTTABLE
    )
    assert type(output["ECHOSTRUCT"]["RFCTIME"]) is str
    assert type(output["RFCTABLE"][0]["RFCTIME"]) is str
    assert output["ECHOSTRUCT"]["RFCTIME"] == TEST_TIME
    assert output["RFCTABLE"][0]["RFCTIME"] == TEST_TIME


def test_time_accepts_time():
    TEST_TIME = ABAP_to_python_time("123456")
    IMPORTSTRUCT = {"RFCTIME": TEST_TIME}
    IMPORTTABLE = [IMPORTSTRUCT]
    output = client.call(
        "STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT, RFCTABLE=IMPORTTABLE
    )
    assert type(output["ECHOSTRUCT"]["RFCTIME"]) is str
    assert type(output["RFCTABLE"][0]["RFCTIME"]) is str
    assert output["ECHOSTRUCT"]["RFCTIME"] == python_to_ABAP_time(TEST_TIME)
    assert output["RFCTABLE"][0]["RFCTIME"] == python_to_ABAP_time(TEST_TIME)


def test_error_int_rejects_string():
    IMPORTSTRUCT = {"RFCINT1": "1"}
    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)
    error = ex.value
    assert error.args[0] == "an integer required, received"
    assert error.args[1] == IMPORTSTRUCT["RFCINT1"]
    assert error.args[3] is str
    assert error.args[4] == "RFCINT1"
    assert error.args[5] == "IMPORTSTRUCT"
    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", RFCTABLE=[IMPORTSTRUCT])
    error = ex.value
    assert error.args[0] == "an integer required, received"
    assert error.args[1] == IMPORTSTRUCT["RFCINT1"]
    assert error.args[3] is str
    assert error.args[4] == "RFCINT1"
    assert error.args[5] == "RFCTABLE"


def test_error_int_rejects_float():
    IMPORTSTRUCT = {"RFCINT1": 1.0}
    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)
    error = ex.value
    assert error.args[0] == "an integer required, received"
    assert error.args[1] == IMPORTSTRUCT["RFCINT1"]
    assert error.args[3] is float
    assert error.args[4] == "RFCINT1"
    assert error.args[5] == "IMPORTSTRUCT"

    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", RFCTABLE=[IMPORTSTRUCT])
    error = ex.value
    assert error.args[0] == "an integer required, received"
    assert error.args[1] == IMPORTSTRUCT["RFCINT1"]
    assert error.args[3] is float
    assert error.args[4] == "RFCINT1"
    assert error.args[5] == "RFCTABLE"


def test_error_string_rejects_None():
    IMPORTSTRUCT = {"RFCCHAR4": None}
    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)
    error = ex.value
    assert error.args[0] == "an string is required, received"
    assert error.args[1] == IMPORTSTRUCT["RFCCHAR4"]
    assert isinstance(None, error.args[3])  # error.args[3] is type(None)
    assert error.args[4] == "RFCCHAR4"
    assert error.args[5] == "IMPORTSTRUCT"
    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", RFCTABLE=[IMPORTSTRUCT])
    error = ex.value
    assert error.args[0] == "an string is required, received"
    assert error.args[1] == IMPORTSTRUCT["RFCCHAR4"]
    assert isinstance(None, error.args[3])  # error.args[3] is type(None)
    assert error.args[4] == "RFCCHAR4"
    assert error.args[5] == "RFCTABLE"


def test_error_string_rejects_int():
    IMPORTSTRUCT = {"RFCCHAR4": 1}
    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)
    error = ex.value
    assert error.args[0] == "an string is required, received"
    assert error.args[1] == IMPORTSTRUCT["RFCCHAR4"]
    assert error.args[3] is int
    assert error.args[4] == "RFCCHAR4"
    assert error.args[5] == "IMPORTSTRUCT"

    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", RFCTABLE=[IMPORTSTRUCT])
    error = ex.value
    assert error.args[0] == "an string is required, received"
    assert error.args[1] == IMPORTSTRUCT["RFCCHAR4"]
    assert error.args[3] is int
    assert error.args[4] == "RFCCHAR4"
    assert error.args[5] == "RFCTABLE"


def test_float_rejects_not_a_number_string():
    IMPORTSTRUCT = {"RFCFLOAT": "A"}
    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)
    error = ex.value
    assert error.args[0] == "a decimal value required, received"
    assert error.args[1] == IMPORTSTRUCT["RFCFLOAT"]
    assert error.args[3] is str
    assert error.args[4] == "RFCFLOAT"
    assert error.args[5] == "IMPORTSTRUCT"


def test_float_rejects_array():
    IMPORTSTRUCT = {"RFCFLOAT": []}
    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)
    error = ex.value
    assert error.args[0] == "a decimal value required, received"
    assert error.args[1] == []
    assert error.args[3] is list
    assert error.args[4] == "RFCFLOAT"
    assert error.args[5] == "IMPORTSTRUCT"


def test_float_rejects_comma_for_point_locale():
    IMPORTSTRUCT = {"RFCFLOAT": "1,2"}
    with pytest.raises(TypeError) as ex:
        client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)
    error = ex.value
    assert error.args[0] == "a decimal value required, received"
    assert error.args[1] == "1,2"
    assert error.args[3] is str
    assert error.args[4] == "RFCFLOAT"
    assert error.args[5] == "IMPORTSTRUCT"


def test_float_accepts_point_for_point_locale():
    IMPORTSTRUCT = {"RFCFLOAT": "1.2"}
    output = client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)["ECHOSTRUCT"]
    assert output["RFCFLOAT"] == 1.2


def test_float_rejects_point_for_comma_locale():
    if sys.platform != "win32":
        setlocale(LC_ALL, "de_DE")
        set_locale_radix(get_locale_radix())
        IMPORTSTRUCT = {"RFCFLOAT": "1.2"}
        with pytest.raises(ExternalRuntimeError) as ex:
            client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)
        error = ex.value
        assert error.code == 22
        assert error.key == "RFC_CONVERSION_FAILURE"
        assert (
            error.message
            == "Cannot convert string value 1.2 at position 1 for the field RFCFLOAT to type RFCTYPE_FLOAT"
        )
        setlocale(LC_ALL, "")


def test_float_accepts_comma_for_comma_locale():
    if sys.platform != "win32":
        setlocale(LC_ALL, "de_DE")
        set_locale_radix(get_locale_radix())
        IMPORTSTRUCT = {"RFCFLOAT": "1,2"}
        output = client.call("STFC_STRUCTURE", IMPORTSTRUCT=IMPORTSTRUCT)["ECHOSTRUCT"]
        assert output["RFCFLOAT"] == 1.2
        setlocale(LC_ALL, "")


def test_bcd_rejects_not_a_number_string():
    IS_INPUT = {"ZDEC": "A"}
    with pytest.raises(TypeError) as ex:
        client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)["ES_OUTPUT"]
    error = ex.value
    assert error.args[0] == "a decimal value required, received"
    assert error.args[1] == IS_INPUT["ZDEC"]
    assert error.args[3] is str
    assert error.args[4] == "ZDEC"
    assert error.args[5] == "IS_INPUT"


def test_numc_rejects_non_string():
    IS_INPUT = {"ZNUMC": 1}
    with pytest.raises(TypeError) as ex:
        client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)["ES_OUTPUT"]
    error = ex.value
    assert error.args[0] == "a numeric string is required, received"
    assert error.args[1] == IS_INPUT["ZNUMC"]
    assert error.args[3] is int
    assert error.args[4] == "ZNUMC"
    assert error.args[5] == "IS_INPUT"


def test_numc_rejects_non_numeric_string():
    IS_INPUT = {"ZNUMC": "a1"}
    with pytest.raises(TypeError) as ex:
        client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)["ES_OUTPUT"]
    error = ex.value
    assert error.args[0] == "a numeric string is required, received"
    assert error.args[1] == IS_INPUT["ZNUMC"]
    assert error.args[3] is str
    assert error.args[4] == "ZNUMC"
    assert error.args[5] == "IS_INPUT"


def test_numc_rejects_empty_string():
    IS_INPUT = {"ZNUMC": ""}
    with pytest.raises(TypeError) as ex:
        client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)["ES_OUTPUT"]
    error = ex.value
    assert error.args[0] == "a numeric string is required, received"
    assert error.args[1] == IS_INPUT["ZNUMC"]
    assert error.args[3] is str
    assert error.args[4] == "ZNUMC"
    assert error.args[5] == "IS_INPUT"


def test_numc_rejects_space_string():
    IS_INPUT = {"ZNUMC": " "}
    with pytest.raises(TypeError) as ex:
        client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)["ES_OUTPUT"]
    error = ex.value
    assert error.args[0] == "a numeric string is required, received"
    assert error.args[1] == IS_INPUT["ZNUMC"]
    assert error.args[3] is str
    assert error.args[4] == "ZNUMC"
    assert error.args[5] == "IS_INPUT"


def test_utclong_accepts_min_max_initial():
    UTCLONG = RFC_MATH["UTCLONG"]
    conn = Connection(**connection_info("QM7"))

    res = conn.call("ZDATATYPES", IV_UTCLONG=UTCLONG["MIN"])
    assert res["EV_UTCLONG"] == UTCLONG["MIN"]

    res = conn.call("ZDATATYPES", IV_UTCLONG=UTCLONG["MAX"])
    assert res["EV_UTCLONG"] == UTCLONG["MAX"]

    res = conn.call("ZDATATYPES", IV_UTCLONG=UTCLONG["INITIAL"])
    assert res["EV_UTCLONG"] == UTCLONG["INITIAL"]

    conn.close()


def test_utclong_rejects_non_string_or_invalid_format():
    UTCLONG = RFC_MATH["UTCLONG"]
    conn = Connection(**connection_info("QM7"))
    with pytest.raises(TypeError) as ex:
        res = conn.call("ZDATATYPES", IV_UTCLONG=1)
    error = ex.value
    assert error.args == (
        "an string is required, received",
        1,
        "of type",
        type(1),
        "IV_UTCLONG",
    )

    with pytest.raises(ExternalRuntimeError) as ex:
        conn.call("ZDATATYPES", IV_UTCLONG="1")
    error = ex.value
    assert error.code == 22
    assert error.key == "RFC_CONVERSION_FAILURE"
    assert error.message == "Cannot convert 1 to RFCTYPE_UTCLONG : illegal format"

    res = conn.call("ZDATATYPES", IV_UTCLONG=UTCLONG["MIN"])
    assert res["EV_UTCLONG"] == UTCLONG["MIN"]

    res = conn.call("ZDATATYPES", IV_UTCLONG=UTCLONG["MAX"])
    assert res["EV_UTCLONG"] == UTCLONG["MAX"]

    conn.close()

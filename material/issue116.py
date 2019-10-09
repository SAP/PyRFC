# -*- coding: utf-8 -*-

from decimal import Decimal
from pyrfc import Connection

MME = {
    "user": "demo",
    "passwd": "welcome",
    "ashost": "10.68.110.51",
    "sysnr": "00",
    "lang": "EN",
    "client": "510",
    "sysid": "MME",
}

ABAP = MME

RFM = "/coe/rbp_fe_datatypes2"

conn = Connection(**ABAP)

# Predefined numeric types: https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/index.htm?file=abenddic_builtin_types_intro.htm
# JavaScript safe integers range https://www.ecma-international.org/ecma-262/8.0/#sec-number.max_safe_integer

RFC_MATH = {
    "RFC_INT1MAX": 255,
    "RFC_INT2MAX": 32768,
    "RFC_INT4MAX": 2147483648,
    "RFC_INT4MAX": 9223372036854775808,
    "FLOAT_MIN": "2.2250738585072014E-308",
    "FLOAT_MAX": "1.7976931348623157E+308",
    "DECF16_MIN": "1E-383",
    "DECF16_MAX": "9.999999999999999E+384",
    "DECF34_MIN": "1E-6143",
    "DECF34_MAX": "9.999999999999999999999999999999999E+6144",
    "RFCINT1": {"MIN": 0, "MAX": 255},
    "RFCINT2": {"MIN": -32768, "MAX": 32767},
    "RFCINT4": {"MIN": -2147483648, "MAX": 2147483647},
    "RFCINT8": {"MIN": -9223372036854775808, "MAX": 9223372036854775807},
    "DECF16_POS": {"MIN": "1E-383", "MAX": "9.999999999999999E+384"},
    "DECF16_NEG": {"MIN": "-1E-383", "MAX": "-9.999999999999999E+384"},
    "DECF34_POS": {
        "MIN": "1E-6143",
        "MAX": "9.999999999999999999999999999999999E+6144",
    },
    "DECF34_NEG": {
        "MIN": "-1E-6143",
        "MAX": "-9.999999999999999999999999999999999E+6144",
    },
    "FLOAT_POS": {"MIN": "2.2250738585072014e-308", "MAX": "1.7976931348623157e+308"},
    "FLOAT_NEG": {"MIN": "-2.2250738585072014e-308", "MAX": "-1.7976931348623157e+308"},
    "DATE": {"MIN": "00010101", "MAX": "99991231"},
    "TIME": {"MIN": "000000", "MAX": "235959"},
}

if __name__ == "__main__":
    try:
        IS_INPUT = {
            # Float
            "ZFLTP_MIN": RFC_MATH["FLOAT_POS"]["MIN"],
            "ZFLTP_MAX": RFC_MATH["FLOAT_POS"]["MAX"],
            # Decimal
            "ZDECF16_MIN": RFC_MATH["DECF16_POS"]["MIN"],
            "ZDECF16_MAX": RFC_MATH["DECF16_POS"]["MAX"],
            "ZDECF34_MIN": RFC_MATH["DECF34_POS"]["MIN"],
            "ZDECF34_MAX": RFC_MATH["DECF34_POS"]["MAX"],
        }
        result = conn.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT)["ES_OUTPUT"]
        for k in IS_INPUT:
            if "FLTP" in k:
                print(k, float(IS_INPUT[k]) == result[k])
            else:
                print(k, Decimal(IS_INPUT[k]) == result[k])
    except Exception as e:
        print(e)

    try:
        IS_INPUT = {
            # Float
            "ZFLTP_MIN": RFC_MATH["FLOAT_NEG"]["MIN"],
            "ZFLTP_MAX": RFC_MATH["FLOAT_NEG"]["MAX"],
            # Decimal
            "ZDECF16_MIN": RFC_MATH["DECF16_NEG"]["MIN"],
            "ZDECF16_MAX": RFC_MATH["DECF16_NEG"]["MAX"],
            "ZDECF34_MIN": RFC_MATH["DECF34_NEG"]["MIN"],
            "ZDECF34_MAX": RFC_MATH["DECF34_NEG"]["MAX"],
        }
        result = conn.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT)["ES_OUTPUT"]
        for k in IS_INPUT:
            if "FLTP" in k:
                print(k, float(IS_INPUT[k]) == result[k])
            else:
                print(k, Decimal(IS_INPUT[k]) == result[k])
    except Exception as e:
        print(e)

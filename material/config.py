# -*- coding: utf-8 -*

import datetime

try:
    from configparser import ConfigParser

    COPA = ConfigParser()
    fc = open("tests/pyrfc.cfg", "r")
    COPA.read_file(fc)
except ImportError as ex:
    from configparser import config_parser

    COPA = config_parser()
    COPA.read_file("tests/pyrfc.cfg")


# Numeric types
#
# ABAP:       https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/index.htm?file=abenddic_builtin_types_intro.htm
# JavaScript: https://www.ecma-international.org/ecma-262/10.0/index.html#Title
#

RFC_MATH = {
    "RFC_INT1": {"MIN": 0, "MAX": 255},
    "RFC_INT2": {"NEG": -32768, "POS": 32767},
    "RFC_INT4": {"NEG": -2147483648, "POS": 2147483647},
    "RFC_INT8": {"NEG": -9223372036854775808, "POS": 9223372036854775807},
    "FLOAT": {
        "NEG": {"MIN": "-2.2250738585072014E-308", "MAX": "-1.7976931348623157E+308"},
        "POS": {"MIN": "2.2250738585072014E-308", "MAX": "1.7976931348623157E+308"},
    },
    "DECF16": {
        "NEG": {"MIN": "-1E-383", "MAX": "-9.999999999999999E+384"},
        "POS": {"MIN": "1E-383", "MAX": "9.999999999999999E+384"},
    },
    "DECF34": {
        "NEG": {"MIN": "-1E-6143", "MAX": "-9.999999999999999999999999999999999E+6144"},
        "POS": {"MIN": "1E-6143", "MAX": "9.999999999999999999999999999999999E+6144"},
    },
    "DATE": {"MIN": "00010101", "MAX": "99991231"},
    "TIME": {"MIN": "000000", "MAX": "235959"},
}


def get_error(ex):
    error = {}
    ex_type_full = str(type(ex))
    error["type"] = ex_type_full[ex_type_full.rfind(".") + 1 : ex_type_full.rfind("'")]
    error["code"] = ex.code if hasattr(ex, "code") else "<None>"
    error["key"] = ex.key if hasattr(ex, "key") else "<None>"
    error["message"] = ex.message.split("\n")
    error["msg_class"] = ex.msg_class if hasattr(ex, "msg_class") else "<None>"
    error["msg_type"] = ex.msg_type if hasattr(ex, "msg_type") else "<None>"
    error["msg_number"] = ex.msg_number if hasattr(ex, "msg_number") else "<None>"
    error["msg_v1"] = ex.msg_v1 if hasattr(ex, "msg_v1") else "<None>"
    return error


def ABAP_to_python_date(abap_date):
    return datetime.datetime.strptime(abap_date, "%Y%m%d").date()


def ABAP_to_python_time(abap_time):
    return datetime.datetime.strptime(abap_time, "%H%M%S").time()


def python_to_ABAP_date(py_date):
    return "{:04d}{:02d}{:02d}".format(py_date.year, py_date.month, py_date.day)


def python_to_ABAP_time(py_time):
    return "{:02d}{:02d}{:02d}".format(py_time.hour, py_time.minute, py_time.second)


CONFIG_SECTIONS = COPA._sections
CONNECTION_INFO = CONFIG_SECTIONS["coevi51"]
UNICODETEST = "ทดสอบสร้างลูกค้าจากภายนอกครั้งที่" * 7

PARAMS = CONNECTION_INFO


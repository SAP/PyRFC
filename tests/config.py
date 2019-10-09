try:
    from configparser import ConfigParser

    COPA = ConfigParser()
    fc = open("tests/pyrfc.cfg", "r")
    COPA.read_file(fc)
except ImportError as ex:
    from configparser import config_parser

    COPA = config_parser()
    COPA.read_file("tests/pyrfc.cfg")

CONFIG_SECTIONS = COPA._sections
PARAMS = CONFIG_SECTIONS["coevi51"]


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


# https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/index.htm?file=abenddic_builtin_types_intro.htm
RFC_MATH = {
    "RFCINT1": {"MIN": 0, "MAX": 255},
    "RFCINT2": {"MIN": -32768, "MAX": 32767},
    "RFCINT4": {"MIN": -2147483648, "MAX": 2147483647},
    "RFCINT8": {"MIN": -9223372036854775808, "MAX": 9223372036854775807},
    "DECF16_POS": {"MIN": "1E-383", "MAX": "9.999999999999999E+384"},
    "DECF34_POS": {
        "MIN": "1E-6143",
        "MAX": "9.999999999999999999999999999999999E+6144",
    },
    "DECF16_NEG": {"MIN": "-1E-383", "MAX": "-1E385"},
    "DECF34_NEG": {"MIN": "-1E6145", "MAX": "-1E-6143"},
    "FLOAT": {"MIN": "-1.7976931348623157E+308", "MAX": "1.7976931348623157E+308"},
    "DATE": {"MIN": "00010101", "MAX": "99991231"},
    "TIME": {"MIN": "000000", "MAX": "235959"},
}


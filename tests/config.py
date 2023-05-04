# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import datetime
from configparser import ConfigParser
import platform
from pyrfc import set_ini_file_directory

COPA = ConfigParser()
with open("tests/pyrfc.cfg", "r") as fc:
    COPA.read_file(fc)

# Numeric types
#
# ABAP:       https://help.sap.com/doc/abapdocu_752_index_htm/7.52/en-US/index.htm?file=abenddic_builtin_types_intro.htm
# JavaScript: https://www.ecma-international.org/ecma-262/10.0/index.html#Title
#

latest_python_version = (
    3,
    11,
)

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
    "UTCLONG": {
        "MIN": "0001-01-01T00:00:00.0000000",
        "MAX": "9999-12-31T23:59:59.9999999",
        "INITIAL": "0000-00-00T00:00:00.0000000",
    },
}


def ABAP_to_python_date(abap_date):
    return datetime.datetime.strptime(abap_date, "%Y%m%d").date()


def ABAP_to_python_time(abap_time):
    return datetime.datetime.strptime(abap_time, "%H%M%S").time()


def python_to_ABAP_date(py_date):
    return f"{py_date.year:04d}{py_date.month:02d}{py_date.day:02d}"


def python_to_ABAP_time(py_time):
    return f"{py_time.hour:02d}{py_time.minute:02d}{py_time.second:02d}"


set_ini_file_directory("tests")

CONFIG_SECTIONS = COPA._sections
CONNECTION_INFO = CONFIG_SECTIONS["coevi51"]
UNICODETEST = "ทดสอบสร้างลูกค้าจากภายนอกครั้งที่" * 7
UNICODE1 = "四周远处都"
BYTEARRAY_TEST = bytearray.fromhex("01414243444549500051fdfeff")
BYTES_TEST = bytes(BYTEARRAY_TEST)
PARAMS = CONNECTION_INFO
PARAMSDEST = {"dest": "MME"}

PLATFORM = platform.system().lower()
CryptoLibPath = {
    "darwin": "/Applications/Secure Login Client.app/Contents/MacOS/lib/libsapcrypto.dylib",
    "linux": "/usr/local/sap/cryptolib/libsapcrypto.so",
    "win32": "C:\\Tools\\cryptolib\\sapcrypto.dll",
    "windows": "C:\\Tools\\cryptolib\\sapcrypto.dll"
    # "C:\\Program Files\\SAP\\FrontEnd\\SecureLogin\\libsapcrypto.dll"
}[PLATFORM]

ClientPSEPath = {
    "darwin": "/Users/d037732/dotfiles/sec/rfctest.pse",
    "linux": "/home/www-admin/sec/rfctest.pse",
    "win32": "C:\\Tools\\sec\\rfctest.pse",
    "windows": "C:\\Tools\\sec\\rfctest.pse",
}[PLATFORM]

LANGUAGES = {
    "AF": {"lang_sap": "a", "text": "Afrikaans"},
    "SQ": {"lang_sap": "뽑", "text": "Albanian"},
    "AG": {"lang_sap": "뢇", "text": "Algonquian"},
    "AR": {"lang_sap": "A", "text": "Arabic"},
    "AZ": {"lang_sap": "뢚", "text": "Azerbaijani"},
    "BD": {"lang_sap": "룤", "text": "Banda"},
    "BB": {"lang_sap": "룢", "text": "Bemba"},
    "BN": {"lang_sap": "룮", "text": "Bengali"},
    "BK": {"lang_sap": "룫", "text": "Bikol"},
    "BS": {"lang_sap": "룳", "text": "Bosnian"},
    "Z9": {"lang_sap": "&", "text": "Brazilian Prtugu"},
    "BG": {"lang_sap": "W", "text": "Bulgarian"},
    "CA": {"lang_sap": "c", "text": "Catalan"},
    "ZH": {"lang_sap": "1", "text": "Chinese"},
    "ZF": {"lang_sap": "M", "text": "Chinese trad."},
    "KW": {"lang_sap": "뱗", "text": "Cornish"},
    "HR": {"lang_sap": "6", "text": "Croatian"},
    "Z1": {"lang_sap": "Z", "text": "Customer reserve"},
    "CS": {"lang_sap": "C", "text": "Czech"},
    "DA": {"lang_sap": "K", "text": "Danish"},
    "NL": {"lang_sap": "N", "text": "Dutch"},
    "DM": {"lang_sap": "릭", "text": "Dutch, Middle"},
    "EN": {"lang_sap": "E", "text": "English"},
    "6N": {"lang_sap": "둮", "text": "English GB"},
    "ET": {"lang_sap": "9", "text": "Estonian"},
    "FI": {"lang_sap": "U", "text": "Finnish"},
    "FR": {"lang_sap": "F", "text": "French"},
    "3F": {"lang_sap": "덆", "text": "French CA"},
    "DE": {"lang_sap": "D", "text": "German"},
    "4G": {"lang_sap": "뎧", "text": "German_CH"},
    "EL": {"lang_sap": "G", "text": "Greek"},
    "HE": {"lang_sap": "B", "text": "Hebrew"},
    "HI": {"lang_sap": "묩", "text": "Hindi"},
    "HU": {"lang_sap": "H", "text": "Hungarian"},
    "IS": {"lang_sap": "b", "text": "Icelandic"},
    "IN": {"lang_sap": "뮎", "text": "Indic"},
    "ID": {"lang_sap": "i", "text": "Indonesian"},
    "IR": {"lang_sap": "뮒", "text": "Iranian"},
    "IT": {"lang_sap": "I", "text": "Italian"},
    "JA": {"lang_sap": "J", "text": "Japanese"},
    "KK": {"lang_sap": "뱋", "text": "Kazakh"},
    "KO": {"lang_sap": "3", "text": "Korean"},
    "LV": {"lang_sap": "Y", "text": "Latvian"},
    "LT": {"lang_sap": "X", "text": "Lithuanian"},
    "MK": {"lang_sap": "봋", "text": "Macedonian"},
    "MS": {"lang_sap": "7", "text": "Malay"},
    "MV": {"lang_sap": "봖", "text": "Manipuri"},
    "MO": {"lang_sap": "봏", "text": "Moldavian"},
    "NI": {"lang_sap": "뵩", "text": "Niger-Kordofa"},
    "NO": {"lang_sap": "O", "text": "Norwegian"},
    "OM": {"lang_sap": "뷍", "text": "Oromo"},
    "P1": {"lang_sap": "븑", "text": "Phillipine"},
    "PL": {"lang_sap": "L", "text": "Polish"},
    "PT": {"lang_sap": "P", "text": "Portuguese"},
    "1P": {"lang_sap": "느", "text": "Portuguese PT"},
    "PK": {"lang_sap": "븫", "text": "Prakrit"},
    "RO": {"lang_sap": "4", "text": "Romanian"},
    "RU": {"lang_sap": "R", "text": "Russian"},
    "SA": {"lang_sap": "뽁", "text": "Sanskrit"},
    "SR": {"lang_sap": "0", "text": "Serbian"},
    "SH": {"lang_sap": "d", "text": "Serbian (Latin)"},
    "SK": {"lang_sap": "Q", "text": "Slovak"},
    "SL": {"lang_sap": "5", "text": "Slovenian"},
    "ES": {"lang_sap": "S", "text": "Spanish"},
    "1X": {"lang_sap": "늘", "text": "Spanish MX"},
    "SV": {"lang_sap": "V", "text": "Swedish"},
    "TA": {"lang_sap": "뾡", "text": "Tamil"},
    "TT": {"lang_sap": "뾴", "text": "Tatar"},
    "1Q": {"lang_sap": "늑", "text": "Technical code 1"},
    "2Q": {"lang_sap": "닱", "text": "Technical code 2"},
    "TH": {"lang_sap": "2", "text": "Thai"},
    "TR": {"lang_sap": "T", "text": "Turkish"},
    "TC": {"lang_sap": "뾣", "text": "Tuvinain"},
    "Z8": {"lang_sap": ";", "text": "US English"},
    "UK": {"lang_sap": "8", "text": "Ukrainian"},
    "VI": {"lang_sap": "쁩", "text": "Vietnamese"},
}

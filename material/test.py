from platform import system, release
from sys import version_info
from configparser import ConfigParser
from pyrfc import Connection, get_nwrfclib_version

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
CONNECTION_INFO = CONFIG_SECTIONS["coevi51"]


conn = Connection(**CONNECTION_INFO)

print("Platform:", system(), release())
print("Python version:", version_info)
print("SAP NW RFC:", get_nwrfclib_version())

str_unicode = "四周远处都能望见"
str_unicode = "四周远处都"
ZRAW = bytes(str_unicode, encoding="utf-8")  # or str_unicode.encode("utf-8")
IS_INPUT = {"ZRAW": ZRAW, "ZRAWSTRING": ZRAW}
output = conn.call("/COE/RBP_FE_DATATYPES2", IV_INT1=1)
print(output)

"""[summary]

result = conn.call('/COE/RBP_PAM_SERVICE_ORD_CHANG', IV_ORDERID='4711', IT_NOTICE_NOTIFICATION=[{'': 'ABCD'}, {'': 'XYZ'}])

for line in result['ET_STRING']:
    print line

for line in result['ET_TABLE']:
    print line

result = conn.call('/COE/RBP_PAM_SERVICE_ORD_CHANG', IV_ORDERID='4711', IT_NOTICE_NOTIFICATION=['ABCD', 'XYZ'])

for line in result['ET_STRING']:
    print line

for line in result['ET_TABLE']:
    print line

"""

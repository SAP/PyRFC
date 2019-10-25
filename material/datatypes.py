# -*- coding: utf-8 -*-
from pyrfc import *
from decimal import Decimal
import datetime
from config import CONNECTION_INFO, RFC_MATH


conn_strip = Connection({"rstrip": True}, **CONNECTION_INFO)
hello = u"Hällo SAP!    "
result = conn_strip.call("STFC_CONNECTION", REQUTEXT=hello)
# assert len(result["RESPTEXT"]) == len(result["ECHOTEXT"])
# self.conn_strip.close()

"""

client = Connection(**CONNECTION_INFO)


uc = u"四周远处都"
uc = u"ÄÜ"
uc = u"fgh"
buc = uc.encode("utf-8")
print(len(uc), uc)
print(len(buc), buc)

ZRAW = buc
IS_INPUT = {"ZRAW": ZRAW, "ZRAWSTRING": ZRAW}
output = client.call("/COE/RBP_FE_DATATYPES", IS_INPUT=IS_INPUT, IV_COUNT=0)[
    "ES_OUTPUT"
]
print(len(ZRAW), ZRAW)
print(len(output["ZRAW"]), output["ZRAW"])


imp = dict(
    RFCFLOAT=1.23456789,
    RFCINT2=0x7FFE,
    RFCINT1=0x7F,
    RFCCHAR4=u"bcde",
    RFCINT4=0x7FFFFFFE,
    RFCHEX3=buc,
    RFCCHAR1=u"a",
    RFCCHAR2=u"ij",
    RFCTIME="123456",  # datetime.time(12,34,56),
    RFCDATE="20161231",  # datetime.date(2011,10,17),
    RFCDATA1=u"k" * 50,
    RFCDATA2=u"l" * 50,
)
result = client.call("STFC_STRUCTURE", IMPORTSTRUCT=imp)["ECHOSTRUCT"]

print(len(result["RFCHEX3"]), result["RFCHEX3"])
"""

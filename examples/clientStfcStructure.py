from pyrfc import Connection

from pprint import pprint
import datetime
from ConfigParser import ConfigParser
import sys

imp = dict(
    RFCINT1=0x7f, # INT1: Integer value (1 byte)
    RFCINT2=0x7ffe, # INT2: Integer value (2 bytes)
    RFCINT4=0x7ffffffe, # INT: integer value (4 bytes)
    RFCFLOAT=1.23456789, # FLOAT

    RFCCHAR1=u'a', # CHAR[1]
    RFCCHAR2=u'ij', # CHAR[2]
    RFCCHAR4=u'bcde', # CHAR[4]
    RFCDATA1=u'k'*50, RFCDATA2=u'l'*50, # CHAR[50] each

    RFCTIME=datetime.time(12,34,56), # TIME
    RFCDATE=datetime.date(2012,10,03), # DATE

    RFCHEX3='\x66\x67\x68' # BYTE[3]: String with 3 hexadecimal values (='fgh')
)

def main():
    config = ConfigParser()
    config.read('sapnwrfc.cfg')
    params_connection = config._sections['connection']

    conn = Connection(**params_connection)
    result = conn.call('STFC_STRUCTURE', IMPORTSTRUCT=imp)
    pprint(result)

if __name__ == '__main__':
    main()

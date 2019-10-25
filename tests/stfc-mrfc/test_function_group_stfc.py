#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import unittest
import pyrfc

from tests.config import PARAMS as params, get_error


class TestSTFC:
    """
    This test cases cover selected functions from the STFC function group.
    """

    def setup_method(self, test_method):
        self.conn = pyrfc.Connection(**params)
        assert self.conn.alive

    def test_info(self):
        connection_info = self.conn.get_connection_attributes()
        assert connection_info["isoLanguage"] == u"EN"

    def teardown_method(self, test_method):
        self.conn.close()
        assert not self.conn.alive

    """
    @unittest.skip("not supported yet (qrfc)")
    def test_STFC_CALL_QRFC(self):
    # STFC_CALL_QRFC qRFC mit Ausgangsqueue in der Verbuchung
        pass

    @unittest.skip("not supported yet (qrfc)")
    def test_STFC_CALL_QRFC_INBOUND(self):
        # STFC_CALL_QRFC_INBOUND qRFC mit Inboundqueue in der Verbuchung
        pass

    @unittest.skip("not supported yet (qrfc)")
    def test_STFC_CALL_QRFC_LOAD_TEST(self):
        # STFC_CALL_QRFC_LOAD_TEST qRFC mit Ausgangsqueue in der Verbuchung
        pass

    @unittest.skip("not supported yet (qrfc)")
    def test_STFC_CALL_QRFC_VB_PING(self):
        # STFC_CALL_QRFC_VB_PING Aufruf eines PING in Update Task
        pass

    @unittest.skip("not supported yet (trfc)")
    def test_STFC_CALL_TRFC(self):
        # STFC_CALL_TRFC tRFC in der Verbuchung
        pass

        # no remote-enabled module
        # def test_STFC_CALL_TRFC_PLUS_UPDATE(self):
        # STFC_CALL_TRFC_PLUS_UPDATE TRFC in VB innerhalb der VB nochmal tRFC
    #    pass
    """

    """
    @unittest.skip("not supported yet (server)")
    def test_STFC_CONNECTION_BACK(self):
        # STFC_CONNECTION_BACK RFC-Test:  CONNECTION Test
        pass

    @unittest.skip("not supported yet (??? VB specific)")
    def test_STFC_INSERT_INTO_TCPIC(self):
        # STFC_INSERT_INTO_TCPIC RFC-TEST:   Insert data into TCPIC running in Update Task
        pass

    @unittest.skip("not supported yet (???)")
    def test_STFC_PERFORMANCE(self):
        # STFC_PERFORMANCE RFC-TEST:   PERFORMANCE Test
        pass

    # This is not remote-enabled; however, we will test the expected error
    def test_STFC_PING_VB(self):
        pass
        # STFC_PING_VB RFC-Ping der in VB gerufen werden kann
        # with self.assertRaises(pyrfc.ABAPRuntimeError) as run:
        #    self.conn.call('STFC_PING_VB')
        # self.assertEqual(run.exception.code, 3)
        # self.assertEqual(run.exception.key, 'CALL_FUNCTION_NOT_REMOTE')

    @unittest.skip("not supported yet (qrfc)")
    def test_STFC_QRFC_TCPIC(self):
        # STFC_QRFC_TCPIC qRFC-Test: Wiederverwendung von qRFC mit Eingangsqueue
        pass

    @unittest.skip("not supported yet (qrfc/trfc)")
    def test_STFC_RETURN_DATA(self):
        # STFC_RETURN_DATA RFC-TEST:   tRFC/qRFC mit Rückmeldestatus und -daten
        pass

    @unittest.skip("not supported yet (qrfc/trfc)")
    def test_STFC_RETURN_DATA_INTERFACE(self):
        # STFC_RETURN_DATA_INTERFACE RFC-TEST:   Schnittstelenbeschreibung für tRFC/qRFC mit Rückmeldedaten
        pass
    """

    """
    @unittest.skip("not supported yet (server)")
    def test_STFC_START_CONNECT_REG_SERVER(self):
        # STFC_START_CONNECT_REG_SERVER RFC-Test:  CONNECTION Test
        pass
    """



    # STFC_STRUCTURE Inhomogene Struktur
    imp = dict(
        RFCFLOAT=1.23456789,
        RFCINT2=0x7FFE,
        RFCINT1=0x7F,
        RFCCHAR4=u"bcde",
        RFCINT4=0x7FFFFFFE,
        RFCHEX3="fgh".encode("utf-8"),
        RFCCHAR1=u"a",
        RFCCHAR2=u"ij",
        RFCTIME="123456",  # datetime.time(12,34,56),
        RFCDATE="20161231",  # datetime.date(2011,10,17),
        RFCDATA1=u"k" * 50,
        RFCDATA2=u"l" * 50,
    )
    out = dict(
        RFCFLOAT=imp["RFCFLOAT"] + 1,
        RFCINT2=imp["RFCINT2"] + 1,
        RFCINT1=imp["RFCINT1"] + 1,
        RFCINT4=imp["RFCINT4"] + 1,
        RFCHEX3=b"\xf1\xf2\xf3",
        RFCCHAR1=u"X",
        RFCCHAR2=u"YZ",
        RFCDATE=str(datetime.date.today()).replace("-", ""),
        RFCDATA1=u"k" * 50,
        RFCDATA2=u"l" * 50,
    )

    """
    def test_ZPYRFC_STFC_STRUCTURE(self):
        # ZYPRFC_STFC_STRUCTURE Inhomogene Struktur
        imp = dict(RFCFLOAT=1.23456789, RFCCHAR1=u'a',
            RFCINT2=0x7ffe, RFCINT1=0x7f,
            RFCCHAR4=u'bcde', RFCINT4=0x7ffffffe,
            RFCHEX3=str.encode('fgh'),
            RFCCHAR2=u'ij',
            RFCTIME=datetime.time(12,34,56),
            RFCDATE=datetime.date(2011,10,17),
            RFCDATA1=u'k'*50, RFCDATA2=u'l'*50,
            RFCNUMC10='1234567890',
            RFCDEC17_8=Decimal('1.32442')
        )
        out = dict(RFCFLOAT=imp['RFCFLOAT']+1, RFCCHAR1=u'X',
            RFCINT2=imp['RFCINT2']+1, RFCINT1=imp['RFCINT1']+1,
            RFCINT4=imp['RFCINT4']+1,
            RFCHEX3=b'\xf1\xf2\xf3',
            RFCCHAR2=u'YZ',
            RFCDATE=datetime.date.today(),
            RFCDATA1=u'k'*50, RFCDATA2=u'l'*50,
            RFCNUMC10='1234512345',
            RFCDEC17_8=Decimal('0')
        )
        result = self.conn.call('ZPYRFC_STFC_STRUCTURE', IMPORTSTRUCT=imp, RFCTABLE=[imp])
        # print result
        self.assertTrue(result['RESPTEXT'].startswith('SAP'))
        assert result['ECHOSTRUCT'] == imp
        assert len(result['RFCTABLE']) == 2
        assert result['RFCTABLE'][0] == imp
        del result['RFCTABLE'][1]['RFCCHAR4'] # contains variable system id
        del result['RFCTABLE'][1]['RFCTIME'] # contains variable server time
        assert result['RFCTABLE'][1] == out

    @unittest.skip("not supported yet (trfc)")
    def test_STFC_TX_TEST(self):
        # STFC_TX_TEST RFC_TEST:  Transaction-oriented RFC (via Update Task)
        pass

    @unittest.skip("not supported yet (trfc)")
    def test_STFC_WRITE_TO_TCPIC(self):
        # STFC_WRITE_TO_TCPIC RFC-TEST:   TRANSACTIONAL RFC
        pass

    # TODO: Purpose???
    def test_STRFC_CHECK_USER_LANGUAGE(self):
        # STRFC_CHECK_USER_LANGUAGE Check User/Language from Client and Server (TCPIC)
        pass

    # TODO: This is not treated. Question: Treated in the c connector?
    # code=4 Error ausgelöst in FB TRFC_RAISE_ERROR Error ausgelöst in FB TRFC_RAISE_ERROR
    def test_TRFC_RAISE_ERROR(self):
        # TRFC_RAISE_ERROR ARFC: Raise different type of error messages
        pass
"""


if __name__ == "__main__":
    unittest.main()

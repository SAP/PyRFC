#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Note: Some test cases for the exception testing are taken from the c-connector test cases
# /bas/BIN/src/krn/rfc/nwrfc/testFramework/clienttests/ExceptionTest.c
# Furthermore, the python script error_test.py in this directory provides more test cases.
# Some of them are used as well.

import unittest
import pyrfc

from tests.config import PARAMS as params, get_error


class TestMRFC:
    """
    This test cases cover selected functions from the MRFC function group.
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
    @unittest.skip("not remote-enabled")
    def test_ABAP4_CALL_TRANSACTION_VB(self):
        # ABAP4_CALL_TRANSACTION_VB
        pass

    @unittest.skip("not remote-enabled")
    def test_IS_VERIRUN_ACTIVE(self):
        # IS_VERIRUN_ACTIVE Determine Whether a Verification Run is Active
        pass

    @unittest.skip("not supported yet (trfc)")
    def test_RFC_CALL_TRANSACTION_USING(self):
        # RFC_CALL_TRANSACTION_USING Verification Program for Execution of RFCs via CALL TRANSACTION USING
        pass

    # ToDo: Class based exceptions
    def test_RFC_CLASS_BASED_EXCP(self):
        # RFC_CLASS_BASED_EXCP RFC mit klassenbasierten Exceptions
        pass

    # TODO: How to test?
    @unittest.skip("not supported yet")
    def test_RFC_PING_AND_WAIT(self):
       # RFC_PING_AND_WAIT Aufruf und Warten
        pass
    """


    """
    @unittest.skip("not remote-enabled")
    def test_RFC_RAISE_ERROR_VB(self):
        # RFC_RAISE_ERROR_VB Behandlung von RFC-Methoden in Verbuchung
        pass

    def test_RFC_TRANSFER_TABLE(self):
        # RFC_TRANSFER_TABLE RFC Test:   PERFORMANCE Test
#         Table input
        pass
#In [45]: h332 = [{'LINE1': 'Hallo', 'LINE2': 'Lise', 'LINE3': 'lauft', 'LINE4': 'leise'}, {'LINE1': 'Hallo', 'LINE2': 'aLise', 'LINE3': 'alauft', 'LINE4': 'aleise'}]
#In [46]: h1000 = [{'LINE1': 'Hallo', 'LINE2': 'Lise', 'LINE3': 'lauft', 'LINE4': 'leise', 'LINE5':'und fuenf'}, {'LINE1': 'Hallo', 'LINE2': 'aLise', 'LINE3': 'alauft', 'LINE4': 'aleise', 'LINE5': 'und sechs'}]
#In [47]: result = conn.call('RFC_TRANSFER_TABLE', APPEND=1, CHECKTAB='y', IMP0332=h332, IMP1000=h1000)


    @unittest.skip("not supported yet (xml)")
    def test_RFC_XML_TEST_1(self):
        # RFC_XML_TEST_1 Test xml stream
        pass

    """


if __name__ == "__main__":
    unittest.main()

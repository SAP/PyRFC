#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import socket
import unittest
import pyrfc

from decimal import Decimal

from tests.config import (
    PARAMS as params,
    CONFIG_SECTIONS as config_sections,
    get_error,
    UNICODETEST,
)


class TestConnection:
    def setup_method(self, test_method):
        self.conn = pyrfc.Connection(**params)
        assert self.conn.alive

    def teardown_method(self, test_method):
        self.conn.close()
        assert not self.conn.alive

    def test_pass_when_not_requested(self):
        PLNTY = "A"
        PLNNR = "00100000"
        NOT_REQUESTED = [
            "ET_COMPONENTS",
            "ET_HDR_HIERARCHY",
            "ET_MPACKAGES",
            "ET_OPERATIONS",
            "ET_OPR_HIERARCHY",
            "ET_PRTS",
            "ET_RELATIONS",
        ]
        result = self.conn.call(
            "EAM_TASKLIST_GET_DETAIL",
            {"not_requested": NOT_REQUESTED},
            IV_PLNTY=PLNTY,
            IV_PLNNR=PLNNR,
        )
        assert len(result["ET_RETURN"]) == 0

    def test_error_when_all_requested(self):
        PLNTY = "A"
        PLNNR = "00100000"
        result = self.conn.call(
            "EAM_TASKLIST_GET_DETAIL", IV_PLNTY=PLNTY, IV_PLNNR=PLNNR
        )
        assert len(result["ET_RETURN"]) == 1
        assert result["ET_RETURN"][0] == {
            "TYPE": "E",
            "ID": "DIWP1",
            "NUMBER": "212",
            "MESSAGE": "Task list A 00100000  is not hierarchical",
            "LOG_NO": "",
            "LOG_MSG_NO": "000000",
            "MESSAGE_V1": "A",
            "MESSAGE_V2": "00100000",
            "MESSAGE_V3": "",
            "MESSAGE_V4": "",
            "PARAMETER": "HIERARCHY",
            "ROW": 0,
            "FIELD": "",
            "SYSTEM": "MMECLNT620",
        }


"""
    def test_many_connections(self):
        # If too many connections are established, the following error will occur (on interactive python shell)
        #
        #CommunicationError: Error 1: [RFC_COMMUNICATION_FAILURE]
        #LOCATION    CPIC (TCP/IP) on local host with Unicode
        #ERROR       max no of 100 conversations exceeded
        #TIME        Tue Sep 18 11:09:35 2012
        #RELEASE     720
        #COMPONENT   CPIC (TCP/IP) with Unicode
        #VERSION     3
        #RC          466
        #MODULE      r3cpic_mt.c
        #LINE        14345
        #COUNTER     1
        # ABAP:
        for i in range(101):
            conn2 = pyrfc.Connection(**params)
            # conn2.close() # Use explicit close() here. If ommitted, the server may block an open connection attempt
                          # _and refuse further connections_, resulting in RFC_INVALID_HANDLE errors for the other
                          # test!


# old tests, referring to non static z-functions
#    def test_invalid_input(self):
#        self.conn.call('Z_PBR_EMPLOYEE_GET', IV_EMPLOYEE='100190', IV_USER_ID='')
#        self.conn.call('Z_PBR_EMPLOYEE_GET', IV_EMPLOYEE='', IV_USER_ID='HRPB_MNG01')
#        self.assertRaises(TypeError, self.conn.call, 'Z_PBR_EMPLOYEE_GET', IV_EMPLOYEE=100190, IV_USER_ID='HRPB_MNG01')
#
#    def test_xstring_output(self):
#        self.conn.call('Z_PBR_EMPLOYEE_GET_XSTRING', IV_EMPLOYEE='100190')
#
#    def test_xstring_input_output(self):
#        for i in 1, 2, 3, 1023, 1024, 1025:
#            s = 'X' * i
#            out = self.conn.call('Z_PBR_TEST_2', IV_INPUT_XSTRING=s)
#            self.assertEqual(s, out['EV_EXPORT_XSTRING'])

"""
if __name__ == "__main__":
    unittest.main()

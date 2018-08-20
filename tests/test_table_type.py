#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import pyrfc
from decimal import Decimal

from tests.config import PARAMS as params, CONFIG_SECTIONS as config_sections, get_error


class TestTT():
    """
    This test cases cover table types of variable and structure types
    """

    def setup_method(self, test_method):
        self.conn = pyrfc.Connection(**params)
        assert self.conn.alive

    def teardown_method(self, test_method):
        self.conn.close()
        assert not self.conn.alive

    def test_TABLE_TYPE(self):
        result = self.conn.call('/COE/RBP_PAM_SERVICE_ORD_CHANG', IV_ORDERID='4711',
                                IT_NOTICE_NOTIFICATION=[{'': 'ABCD'}, {'': 'XYZ'}])
        assert len(result['ET_RETURN']) > 0
        erl = result['ET_RETURN'][0]
        assert erl['TYPE'] == 'E'
        assert erl['ID'] == 'IWO_BAPI'
        assert erl['NUMBER'] == '121'
        assert erl['MESSAGE_V1'] == '4711'


if __name__ == '__main__':
    unittest.main()

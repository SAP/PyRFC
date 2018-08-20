#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
import socket
import pyrfc

import pytest

from tests.config import PARAMS as params, CONFIG_SECTIONS as config_sections, get_error


def utf8len(s):
    return len(s.encode('utf-8'))


class TestIssues():

    def setup_method(self, test_method):
        """ A connection to an SAP backend system
              Instantiating an :class:`pyrfc.Connection` object will
              automatically attempt to open a connection the SAP backend.
              :param config: Configuration of the instance. Allowed keys are:
                    ``dtime``
                      returns datetime types (accepts strings and datetimes), default is False
                    ``rstrip``
                      right strips strings returned from RFC call (default is True)
                    ``return_import_params``
                      importing parameters are returned by the RFC call (default is False)
              :type config: dict or None (default)
        """
        self.conn = pyrfc.Connection(**params)
        assert self.conn.alive

    def test_info(self):
        connection_info = self.conn.get_connection_attributes()
        assert connection_info['isoLanguage'] == u'EN'

    def teardown_method(self, test_method):
        self.conn.close()
        assert not self.conn.alive

    def test_issue31(self):
        """
        This test cases covers the issue 31
        """
        '''
        filename = 'tests/data/issue31/rfcexec.exe'
        block = 1024

        with open(filename, 'rb') as file1:
            send = file1.read()

        send_content = [{'': bytearray(send[i:i+block])} for i in range(0, len(send), block)]

        result = self.conn.call('ZTEST_RAW_TABLE', TT_TBL1024=send_content)

        content = bytearray()
        for line in send_content:
            content += line['']

        assert send == content

        received_content = bytearray()
        for line in result['TT_TBL1024']:
            received_content += line['LINE']

        assert type(content) is bytearray
        assert type(content) == type(received_content)
        received_content = received_content[:len(content)]
        assert len(content) == len(received_content)
        assert content == received_content
        '''

    def test_issue38(self):
        test = [
            'string',
            u'四周远处都能望见',
            u'\U0001F4AA',
            u'\u0001\uf4aa',
            u'a\xac\u1234\u20ac\U0001F4AA'
        ]

        for s in test:
            is_input = {'ZSHLP_MAT1': s, 'ZFLTP': 123.45}
            result = self.conn.call(
                '/COE/RBP_FE_DATATYPES', IS_INPUT=is_input)['ES_OUTPUT']
            assert is_input['ZSHLP_MAT1'] == result['ZSHLP_MAT1']

    def test_issue40(self):
        '''
        # put in cache
        result = self.conn.call('BAPI_USER_GET_DETAIL', USERNAME="DEMO")

        # get from cache
        fd = self.conn.func_desc_get_cached('S16', 'BAPI_USER_GET_DETAIL')
        assert fd.__class__ is pyrfc._pyrfc.FunctionDescription

        # remove from cache

        self.conn.func_desc_remove('S16', 'BAPI_USER_GET_DETAIL')
        try:
            fd = self.conn.func_desc_get_cached('S16', 'BAPI_USER_GET_DETAIL')
            assert fd.__class__ is not 'pyrfc._pyrfc.FunctionDescription'
        except pyrfc.RFCError as ex:
            error = get_error(ex)
            assert error['code'] == 17
            assert error['key'] == 'RFC_NOT_FOUND'
            '''


if __name__ == '__main__':
    unittest.main()

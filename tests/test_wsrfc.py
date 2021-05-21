#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

import unittest
from pyrfc import Connection, set_cryptolib_path, ExternalRuntimeError
from tests.config import (
    CryptoLibPath,
    ClientPSEPath,
)


class TestWsrfc:
    def test_load_cryptolib_success(self):
        assert set_cryptolib_path(CryptoLibPath) is None

    def test_load_cryptolib_error(self):
        wrongPath = "_" + CryptoLibPath
        try:
            assert set_cryptolib_path(wrongPath)
        except Exception as ex:
            assert isinstance(ex, TypeError) is True
            assert ex.args[0] == "Crypto library not found:"
            assert ex.args[1] == wrongPath

    def test_wsrfc_call_no_client_pse(self):
        try:
            client = Connection(dest="WS_ALX_NOCC")
        except Exception as ex:
            assert isinstance(ex, ExternalRuntimeError) is True
            assert ex.code == 20
            assert ex.key == "RFC_INVALID_PARAMETER"
            assert ex.message == "Unable to use TLS with client PSE missing"

    def test_wsrfc_call_basic_auth(self):
        client = Connection(dest="WS_ALX")
        assert client.alive is True
        client.close()

    def test_wsrfc_call_client_cert(self):
        client = Connection(dest="WS_ALX_CC")
        assert client.alive is True
        client.close()


if __name__ == "__main__":
    unittest.main()

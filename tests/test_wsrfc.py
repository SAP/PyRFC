#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

import pytest
from pyrfc import Connection, set_cryptolib_path, ExternalRuntimeError
from tests.config import (
    CryptoLibPath,
    # ClientPSEPath,
)


class TestWsrfc:
    @pytest.mark.skip(reason="no automatic test")
    def test_load_cryptolib_success(self):
        assert set_cryptolib_path(CryptoLibPath) is None

    def test_load_cryptolib_error(self):
        wrongPath = "_" + CryptoLibPath
        with pytest.raises(TypeError) as ex:
            assert set_cryptolib_path(wrongPath)
        error = ex.value
        assert error.args[0] == "Crypto library not found:"
        assert error.args[1] == wrongPath

    def test_wsrfc_call_no_client_pse(self):
        with pytest.raises(ExternalRuntimeError) as ex:
            Connection(dest="WS_ALX_NOCC")
        error = ex.value
        assert error.code == 20
        assert error.key == "RFC_INVALID_PARAMETER"
        assert error.message == "Unable to use TLS with client PSE missing"

    @pytest.mark.skip(reason="no automatic test")
    def test_wsrfc_call_basic_auth(self):
        client = Connection(dest="WS_ALX")
        assert client.alive is True
        client.close()

    @pytest.mark.skip(reason="no automatic test")
    def test_wsrfc_call_client_cert(self):
        client = Connection(dest="WS_ALX_CC")
        assert client.alive is True
        client.close()

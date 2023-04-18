#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

import pytest
from threading import Timer
from pyrfc import Connection, cancel_connection, RFCError

from tests.config import CONNECTION_INFO

client = Connection(**CONNECTION_INFO)


class TestCancel:
    def test_connection_cancel_pyrfc(self):
        old_handle = client.handle
        with pytest.raises(RFCError) as ex:
            # Cancel next RFC call after 5 seconds
            Timer(5, cancel_connection, args=(client,)).start()
            # RFC call taking 10 seconds
            r = client.call("RFC_PING_AND_WAIT", SECONDS=10)
        error = ex.value
        # assert error.group == 4
        assert error.code == 7
        assert error.key == "RFC_CANCELED"
        assert "Connection was canceled" in error.message
        # ensure new connection replaced the cancelled one
        assert client.alive is True
        assert client.handle != old_handle

    def test_connection_cancel_client(self):
        old_handle = client.handle
        with pytest.raises(RFCError) as ex:
            # Cancel next RFC call after 5 seconds
            Timer(5, client.cancel).start()
            # RFC call taking 10 seconds
            r = client.call("RFC_PING_AND_WAIT", SECONDS=10)
        error = ex.value
        # assert error.group == 4
        assert error.code == 7
        assert error.key == "RFC_CANCELED"
        assert "Connection was canceled" in error.message
        # ensure new connection replaced the cancelled one
        assert client.alive is True
        assert client.handle != old_handle

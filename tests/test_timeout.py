# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import pytest
from pyrfc import Connection, RFCError, ExternalRuntimeError

from tests.config import CONNECTION_DEST

client = Connection(**CONNECTION_DEST)


class TestTimeout:
    def test_timeout_call(self):
        with pytest.raises(RFCError) as ex:
            # Cancel 10 seconds long RFC call after 5 seconds
            client.call(
                "RFC_PING_AND_WAIT",
                options={"timeout": 5},
                SECONDS=10,
            )
        error = ex.value
        assert error.code == 7
        assert error.key == "RFC_CANCELED"
        assert "Connection was canceled" in error.message
        # ensure new connection replaced the canceled one
        assert client.alive is True

    def test_timeout_call_expired(self):
        old_handle = client.handle
        # Cancel 5 seconds long RFC call after 10 seconds
        res = client.call("RFC_PING_AND_WAIT", options={"timeout": 10}, SECONDS=5)
        assert res == {}
        assert client.alive is True
        assert client.handle == old_handle

    def test_timeout_connection(self):
        client = Connection(**CONNECTION_DEST, config={"timeout": 5})
        with pytest.raises(RFCError) as ex:
            # Cancel 10 seconds long RFC call after 5 seconds, set on connection
            client.call("RFC_PING_AND_WAIT", SECONDS=10)
        error = ex.value
        assert error.code == 7
        assert error.key == "RFC_CANCELED"
        assert "Connection was canceled" in error.message
        # ensure new connection replaced the cancelled one
        assert client.alive is True

    def test_timeout_connection_override(self):
        client = Connection(**CONNECTION_DEST, config={"timeout": 15})
        with pytest.raises(RFCError) as ex:
            # Cancel 10 seconds long RFC call after 5 seconds, set on call
            client.call(
                "RFC_PING_AND_WAIT",
                options={"timeout": 5},
                SECONDS=10,
            )
        error = ex.value
        assert error.code == 7
        assert error.key == "RFC_CANCELED"
        assert "Connection was canceled" in error.args[0]
        # ensure new connection replaced the canceled one
        assert client.alive is True

    def test_timeout_with_rfc_error(self):
        with pytest.raises(ExternalRuntimeError) as ex:
            client.call("STFC_CONNECTION", options={"timeout": 60}, undefined=0)
        error = ex.value
        assert error.code == 20
        assert error.key == "RFC_INVALID_PARAMETER"
        assert error.message == "field 'undefined' not found"

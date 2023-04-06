# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

import pytest
from pyrfc import Connection, Throughput

from tests.config import PARAMS as params


def equal_no_time(a, b):
    counters = [
        "numberOfCalls",
        "sentBytes",
        "receivedBytes",
        # "applicationTime",
        # "totalTime",
        # "serializationTime",
        # "deserializationTime",
    ]
    for c in counters:
        if a[c] != b[c]:
            return (c, a[c], b[c])
    return True


class TestThroughput:
    def test_create_without_connection(self):
        throughput = Throughput()
        assert len(throughput.connections) == 0

    def test_create_with_single_connection(self):
        conn = Connection(**params)
        throughput = Throughput(conn)
        assert len(throughput.connections) == 1
        conn.close()

    def test_create_with_multiple_connection(self):
        c1 = Connection(**params)
        c2 = Connection(**params)
        throughput = Throughput([c1, c2])
        assert len(throughput.connections) == 2
        throughput = Throughput([c1, c1])
        assert len(throughput.connections) == 1
        c1.close()
        c2.close()

    def test_remove_from_connection(self):
        c1 = Connection(**params)
        c2 = Connection(**params)
        throughput = Throughput([c1, c2])
        assert len(throughput.connections) == 2
        throughput.removeFromConnection(c2)
        assert len(throughput.connections) == 1
        assert next(iter(throughput.connections)) == c1
        c1.close()
        c2.close()

    def test_create_with_invalid_connection(self):
        conn = Connection(**params)
        with pytest.raises(Exception) as ex:
            Throughput(1)
        error = ex.value
        assert isinstance(error, TypeError) is True
        assert error.args == (
            "Connection object required, received",
            1,
            "of type",
            type(1),
        )

        with pytest.raises(Exception) as ex:
            Throughput([conn, 1])
        error = ex.value
        assert isinstance(error, TypeError) is True
        assert error.args == (
            "Connection object required, received",
            1,
            "of type",
            type(1),
        )
        conn.close()

    def test_get_from_connection(self):
        c1 = Connection(**params)
        c2 = Connection(**params)

        x = Throughput(c1)
        y = Throughput(c2)
        z = Throughput.getFromConnection(c1)
        assert z == x
        z = Throughput.getFromConnection(c2)
        assert z == y
        c1.close()
        c2.close()

    def test_throutput_single_connection(self):
        conn = Connection(**params)
        assert conn.alive

        throughput = Throughput()
        throughput.setOnConnection(conn)
        assert throughput.stats == {
            "numberOfCalls": 0,
            "sentBytes": 0,
            "receivedBytes": 0,
            "applicationTime": 0,
            "totalTime": 0,
            "serializationTime": 0,
            "deserializationTime": 0,
        }

        conn.call("STFC_CONNECTION", REQUTEXT="hello")
        assert equal_no_time(
            throughput.stats,
            {
                "numberOfCalls": 2,
                "sentBytes": 1089,
                "receivedBytes": 2812,
                "applicationTime": 0,
                "totalTime": 387,
                "serializationTime": 0,
                "deserializationTime": 0,
            },
        )

        conn.call("STFC_CONNECTION", REQUTEXT="hello")
        assert equal_no_time(
            throughput.stats,
            {
                "numberOfCalls": 3,
                "sentBytes": 1737,
                "receivedBytes": 4022,
                "applicationTime": 0,
                "totalTime": 410,
                "serializationTime": 0,
                "deserializationTime": 0,
            },
        )

        throughput.reset()
        assert equal_no_time(
            throughput.stats,
            {
                "numberOfCalls": 0,
                "sentBytes": 0,
                "receivedBytes": 0,
                "applicationTime": 0,
                "totalTime": 0,
                "serializationTime": 0,
                "deserializationTime": 0,
            },
        )

        conn.call("BAPI_USER_GET_DETAIL", USERNAME="demo")["LASTMODIFIED"]
        assert equal_no_time(
            throughput.stats,
            {
                "numberOfCalls": 90,
                "sentBytes": 67028,
                "receivedBytes": 416456,
                "applicationTime": 0,
                "totalTime": 4833,
                "serializationTime": 2,
                "deserializationTime": 32,
            },
        )

        conn.close()
        assert not conn.alive

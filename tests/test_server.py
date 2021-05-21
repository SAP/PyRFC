#!/usr/bin/env python

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

# -*- coding: utf-8 -*-

import unittest
import os
import pytest
from pyrfc import Server, set_ini_file_directory, ABAPApplicationError

from tests.config import get_error


def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc invoked")
    print("request_context", request_context)
    print(f"REQUTEXT: {REQUTEXT}")

    return {"ECHOTEXT": REQUTEXT, "RESPTEXT": "Python server here"}


dir_path = os.path.dirname(os.path.realpath(__file__))
set_ini_file_directory(dir_path)

server = Server({"dest": "gateway"}, {"dest": "MME"})


class TestServer:
    def teardown_method(self, test_method):
        pass

    def test_add_wrong_function(self):
        try:
            server.add_function("STFC_CONNECTION1", my_stfc_connection)
        except ABAPApplicationError as ex:
            error = get_error(ex)
            assert error["code"] == 5
            assert error["key"] == "FU_NOT_FOUND"
            assert error["message"][0] == "ID:FL Type:E Number:046 STFC_CONNECTION1"

    def test_add_function_twice(self):
        try:
            server.add_function("STFC_CONNECTION", my_stfc_connection)
            server.add_function("STFC_CONNECTION", my_stfc_connection)
        except TypeError as ex:
            assert ex.args[0] == "Server function 'STFC_CONNECTION' already installed."

    @pytest.mark.skip(reason="only manual test for the time being")
    def test_stfc_connection(self):
        print("\nPress CTRL-C to skip server test...")
        server.serve()

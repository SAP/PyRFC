# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import os
import sys
from time import sleep

import pytest
from pyrfc import (
    ABAPApplicationError,
    Connection,
    RCStatus,
    RFCError,
    Server,
    set_ini_file_directory,
)

sys.path.append(os.path.dirname(__file__))
from data.func_desc_BAPISDORDER_GETDETAILEDLIST import (
    FUNC_DESC_BAPISDORDER_GETDETAILEDLIST,
)
from data.func_desc_BS01_SALESORDER_GETDETAIL import (
    FUNC_DESC_BS01_SALESORDER_GETDETAIL,
)
from data.func_desc_STFC_STRUCTURE import FUNC_DESC_STFC_STRUCTURE
from function_description_utils import compare_function_description


def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc invoked")
    print(
        "request_context",
        request_context,
    )
    print(f"REQUTEXT: {REQUTEXT}")

    return {
        "ECHOTEXT": REQUTEXT,
        "RESPTEXT": "Python server here",
    }


dir_path = os.path.dirname(os.path.realpath(__file__))
set_ini_file_directory(dir_path)

server = Server(
    server_params={"dest": "gateway"},
    client_params={"dest": "MME"},
)

client = Connection(dest="MME")


@pytest.mark.skipif(
    not sys.platform.startswith("darwin"), reason="Manual server test on Darwin only"
)
class TestServer:
    def test_add_wrong_function(self):
        with pytest.raises(ABAPApplicationError) as ex:
            server.add_function("STFC_CONNECTION1", my_stfc_connection)
        error = ex.value
        assert error.code == 5
        assert error.key == "FU_NOT_FOUND"
        assert error.message == "ID:FL Type:E Number:046 STFC_CONNECTION1"

    def test_add_function_twice(self):
        with pytest.raises(RFCError) as ex:
            server.add_function("STFC_CONNECTION", my_stfc_connection)
            server.add_function("STFC_CONNECTION", my_stfc_connection)
        error = ex.value
        assert error.args[0] == "Server function 'STFC_CONNECTION' already installed."

    def test_function_description_STFC_STRUCTURE(self):
        func_name = "STFC_STRUCTURE"
        func_desc = client.get_function_description(func_name)
        compare_function_description(
            func_desc,
            FUNC_DESC_STFC_STRUCTURE,
        )

    def test_function_description_BAPISDORDER_GETDETAILEDLIST(self):
        func_name = "BAPISDORDER_GETDETAILEDLIST"
        func_desc = client.get_function_description(func_name)
        compare_function_description(
            func_desc,
            FUNC_DESC_BAPISDORDER_GETDETAILEDLIST,
        )

    def test_function_description_BS01_SALESORDER_GETDETAIL(self):
        func_name = "BS01_SALESORDER_GETDETAIL"
        func_desc = client.get_function_description(func_name)
        compare_function_description(
            func_desc,
            FUNC_DESC_BS01_SALESORDER_GETDETAIL,
        )

    def test_stfc_structure(self):
        def my_stfc_structure(request_context=None, IMPORTSTRUCT=None, RFCTABLE=None):
            """Server function my_stfc_structure with the signature
            of ABAP function module STFC_STRUCTURE."""

            print("stfc structure invoked")
            print("request_context", request_context)
            if IMPORTSTRUCT is None:
                IMPORTSTRUCT = {}
            if RFCTABLE is None:
                RFCTABLE = []
            ECHOSTRUCT = IMPORTSTRUCT.copy()
            ECHOSTRUCT["RFCINT1"] += 1
            ECHOSTRUCT["RFCINT2"] += 1
            ECHOSTRUCT["RFCINT4"] += 1
            if len(RFCTABLE) == 0:
                RFCTABLE = [ECHOSTRUCT]
            RESPTEXT = f"Python server sends {len(RFCTABLE)} table rows"
            print(f"ECHOSTRUCT: {ECHOSTRUCT}")
            print(f"RFCTABLE: {RFCTABLE}")
            print(f"RESPTEXT: {RESPTEXT}")

            return {
                "ECHOSTRUCT": ECHOSTRUCT,
                "RFCTABLE": RFCTABLE,
                "RESPTEXT": RESPTEXT,
            }

        def authentication_check(func_name=False, request_context=None):
            if request_context is None:
                request_context = {}
            print(
                f"[js] authorization '{func_name}' request_context",
                request_context,
            )
            return RCStatus.OK

        def authorization_check(rfcHandle=None, securityAttributes=None):
            print(f"[js] authorization for {rfcHandle}, attr {securityAttributes}")
            return RCStatus.OK

        # create server
        server = Server(
            server_params={"dest": "MME_GATEWAY"},
            client_params={"dest": "MME"},
            config={
                "authentication_check": authentication_check,
                "authorization_check": authorization_check,
                "check_date": False,
                "check_time": False,
                "server_log": True,
            },
        )

        # expose python function my_stfc_structure as ABAP function STFC_STRUCTURE,
        server.add_function("STFC_STRUCTURE", my_stfc_structure)

        # start server
        server.start()

        # call ABAP function module which will call Python server
        # and return the server response
        client = Connection(dest="MME")
        result = client.call("ZSERVER_TEST_STFC_STRUCTURE")

        # shutdown server
        server.close()

        # check the server response
        assert result["RESPTEXT"] == "Python server sends 1 table rows"
        assert "ECHOSTRUCT" in result
        assert result["ECHOSTRUCT"]["RFCINT1"] == 2
        assert result["ECHOSTRUCT"]["RFCINT2"] == 3
        assert result["ECHOSTRUCT"]["RFCINT4"] == 5
        assert result["ECHOSTRUCT"]["RFCDATE"] == "20230928"
        assert result["ECHOSTRUCT"]["RFCTIME"] == "240000"

    def test_trfc(self):
        def stfc_write_to_tcpic(request_context=None, RESTART_QNAME="", TCPICDAT=[]):
            context = (
                {"error": "No request context"}
                if request_context is None
                else request_context["server_context"]
            )
            print("[js] python function: stfc_write_to_tcpic", f"context {context}")
            return {"TCPICDAT": TCPICDAT}

        def onCheckTransaction(rfcHandle, tid):
            print("[js] onCheckTransaction", rfcHandle, tid)
            return RCStatus.OK

        def onCommitTransaction(rfcHandle, tid):
            print("[js] onCommitTransaction", rfcHandle, tid)
            return RCStatus.OK

        def onConfirmTransaction(rfcHandle, tid):
            print("[js] onConfirmTransaction", rfcHandle, tid)
            return RCStatus.OK

        def onRollbackTransaction(rfcHandle, tid):
            print("[js] onRollbackTransaction", rfcHandle, tid)
            return RCStatus.OK

        def authenticationHandler(function_name, server_context=None):
            print(f"[js] authentication for {function_name}, context {server_context}")
            return RCStatus.OK

        def authorizationHandler(rfcHandle=None, securityAttributes=None):
            print(
                f"[js] authorization for {rfcHandle}, security attr {securityAttributes}"
            )
            return RCStatus.OK

        try:
            # Create server
            server = Server(
                server_params={"dest": "MME_GATEWAY"},
                client_params={"dest": "MME"},
                config={"check_date": False, "check_time": False, "server_log": False},
            )

            # ABAP function used to send IDocs via tRFC/qRFC
            server.add_function("STFC_WRITE_TO_TCPIC", stfc_write_to_tcpic)

            # Register the RFC transaction handlers.
            server.transaction_rfc_init(
                sysId="MME",
                transactionHandler={
                    "check": onCheckTransaction,
                    "commit": onCommitTransaction,
                    "rollback": onRollbackTransaction,
                    "confirm": onConfirmTransaction,
                },
            )

            # Start server
            server.start()

            # call RSARFCT0
            client = Connection(dest="MME")
            tcall = "00001"
            ncall = client.call("ZSERVER_TEST_TRFC", NCALL=tcall)["EV_NCALL"]
            client.close()
            assert ncall == tcall

            # receive queues from abap system
            sleep(5)

        except Exception as ex:
            print(ex)
        finally:
            # Shutdown server
            server.close()


def teardown():
    server.close()

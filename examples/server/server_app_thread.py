# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

from threading import Thread

from pyrfc import Server


def my_stfc_connection(request_context=None, REQUTEXT=""):
    """Server function my_stfc_connection with the signature of ABAP function module STFC_CONNECTION."""

    print("stfc connection invoked")
    print("request_context", request_context)
    print(f"REQUTEXT: {REQUTEXT}")

    return {
        "ECHOTEXT": REQUTEXT,
        "RESPTEXT": "Python server here",
    }


def my_auth_check(func_name=False, request_context=None):
    """Server authorization check."""

    if request_context is None:
        request_context = {}
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0


def launch_server():
    """Start server."""

    # create server for ABAP system ABC
    server = Server(
        {"dest": "gateway"},
        {"dest": "MME"},
        {
            "port": 8081,
            "server_log": False,
        },
    )
    print(server.get_server_attributes())

    # expose python function my_stfc_connection as ABAP function STFC_CONNECTION, to be called by ABAP system
    server.add_function(
        "STFC_CONNECTION",
        my_stfc_connection,
    )

    # start server
    server.serve()

    # get server attributes
    print(server.get_server_attributes())


server_thread = Thread(target=launch_server)
server_thread.start()

input("Press Enter to stop server...")  # WPS110

# stop server
server_thread.join()
print("Server  stoped")

# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import os

from pyrfc import RCStatus, Server, set_ini_file_directory


# server function
def my_stfc_connection(
    request_context=None,
    REQUTEXT="",
):
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


# server authorisation check
def my_auth_check(
    func_name=False,
    request_context=None,
):
    print(f"authorization check for '{func_name}'")
    print(
        "request_context",
        request_context or {},
    )
    return RCStatus.OK


dir_path = os.path.dirname(os.path.realpath(__file__))
set_ini_file_directory(dir_path)

# create server instance
server = Server(
    server_params={"dest": "gateway"},
    client_params={"dest": "MME"},
    config={
        "port": 8081,
        "server_log": False,
    },
)

# expose python function my_stfc_connection as ABAP function STFC_CONNECTION,
# that ABAP server can call
server.add_function("STFC_CONNECTION", my_stfc_connection)

try:
    server.start()

    input("Press Enter to stop server...\n")

    server.stop()
except Exception as ex:
    print(ex)

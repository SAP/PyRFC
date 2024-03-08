# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import sys

from backends import BACKEND
from pyrfc import Server

backend_dest = sys.argv[1]

errorInfo = {
    "code": 4,
    "key": "Function not supported",
    "message": "",
    "msg_class": "SR",
    "msg_type": "A",
    "msg_number": "006",
    "msg_v1": "",
    "msg_v2": "",
    "msg_v3": "",
    "msg_v4": "",
}


def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc connection invoked")
    print("request_context", request_context)
    print(f"REQUTEXT: {REQUTEXT}")

    # raise ExternalRuntimeError(**errorInfo)
    # raise ABAPRuntimeError(**errorInfo)
    # raise ABAPApplicationError(**errorInfo)

    return {"ECHOTEXT": REQUTEXT, "RESPTEXT": "Python server here"}


# create server
server = Server(*BACKEND[backend_dest])

# expose python function my_stfc_connection as ABAP function STFC_CONNECTION,
# to be called by ABAP system
server.add_function("STFC_CONNECTION", my_stfc_connection)

# start server
server.start()

input("Press Enter to stop server...")

# stop server
server.stop()
print("Server stoped")

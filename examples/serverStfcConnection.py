# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

import os

from pyrfc import Server, set_ini_file_directory


def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc invoked")
    print("request_context", request_context)
    print("REQUTEXT: {REQUTEXT}")
    return {"ECHOTEXT": REQUTEXT, "RESPTEXT": "Python server here"}


dir_path = os.path.dirname(os.path.realpath(__file__))
set_ini_file_directory(dir_path)

server = Server({"dest": "gateway"}, {"dest": "MME"})

server.add_function("STFC_CONNECTION", my_stfc_connection)

print("\nPress CTRL-C to skip server test...")
server.serve(20)

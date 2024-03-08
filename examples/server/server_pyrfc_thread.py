# SPDX-FileCopyrightText: 2013 SAP SE Srdjan Boskovic <srdjan.boskovic@sap.com>
#
# SPDX-License-Identifier: Apache-2.0

from pyrfc import Server


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

    return {"ECHOSTRUCT": ECHOSTRUCT, "RFCTABLE": RFCTABLE, "RESPTEXT": RESPTEXT}


def my_auth_check(func_name=False, request_context=None):
    """Server authorization check."""

    if request_context is None:
        request_context = {}
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0


# create server
server = Server(
    server_params={"dest": "MME_GATEWAY"},
    client_params={"dest": "MME"},
    config={"check_date": False, "check_time": False, "server_log": True},
)

print(server.options)

# expose python function my_stfc_structure as ABAP function STFC_STRUCTURE
# to be called from ABAP system
server.add_function("STFC_STRUCTURE", my_stfc_structure)

# start server
server.start()

# get server attributes
print(server.get_server_attributes())

input("Press Enter to stop server...")

# shutdown server
server.close()

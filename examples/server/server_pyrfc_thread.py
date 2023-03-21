import os
from pyrfc import Server

# server functions

def my_stfc_structure(request_context=None, IMPORTSTRUCT={}, RFCTABLE=[]):
    print("stfc structure invoked")
    print("request_context", request_context)
    ECHOSTRUCT = IMPORTSTRUCT
    if len(RFCTABLE) == 0: RFCTABLE = [ECHOSTRUCT]
    RESPTEXT = f"Python server response: {ECHOSTRUCT['RFCINT1']}, table rows: {len(RFCTABLE)}"
    print(f"ECHOSTRUCT: {ECHOSTRUCT}")
    print(f"RFCTABLE: {RFCTABLE}")
    print(f"RESPTEXT: {RESPTEXT}")

    return {"ECHOSTRUCT": ECHOSTRUCT, "RFCTABLE": RFCTABLE, "RESPTEXT": RESPTEXT}

# server authorisation check

def my_auth_check(func_name=False, request_context={}):
    print(f"authorization check for '{func_name}'")
    print("request_context", request_context)
    return 0

# create server
server = Server({"dest": "gateway"}, {"dest": "MME"}, {"port": 8081, "server_log": False})

# expose python function my_stfc_structure as ABAP function STFC_STRUCTURE, to be called by ABAP system
server.add_function("STFC_STRUCTURE", my_stfc_structure)

# start server
server.start()

# get server attributes
print(server.get_server_attributes())

input("Press Enter to stop server...")

# stop server
server.stop()
print("Server stoped")

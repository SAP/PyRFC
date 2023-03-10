import sys
from pyrfc import Server
from threading import Thread
from backends import BACKEND

backend_dest = sys.argv[1]

# server functions

def my_stfc_connection(request_context=None, REQUTEXT=""):
    print("stfc connection invoked")
    print("request_context", request_context)
    print(f"REQUTEXT: {REQUTEXT}")

    return {"ECHOTEXT": REQUTEXT, "RESPTEXT": "Python server here"}

def my_stfc_structure(request_context=None, IMPORTSTRUCT={}, RFCTABLE=[]):
    print("stfc structure invoked")
    print("request_context", request_context)
    ECHOSTRUCT = IMPORTSTRUCT
    if len(RFCTABLE) == 0:
        RFCTABLE = [ECHOSTRUCT]
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

def server_serve(sid):
    server = Server(*BACKEND[sid])
    print(server.get_server_attributes())

    # expose python function my_stfc_connection as ABAP function STFC_CONNECTION, to be called by ABAP system
    server.add_function("STFC_CONNECTION", my_stfc_connection)

    # expose python function my_stfc_structure as ABAP function STFC_STRUCTURE, to be called by ABAP system
    server.add_function("STFC_STRUCTURE", my_stfc_structure)

    # start server
    server.serve()

# start server

server_thread = Thread(target=server_serve(backend_dest))
server_thread.start()

input("Press Enter to stop server...")

server_thread.join()

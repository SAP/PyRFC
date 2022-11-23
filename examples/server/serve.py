import os
from pyrfc import Server, set_ini_file_directory
from threading import Thread

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

dir_path = os.path.dirname(os.path.realpath(__file__))
set_ini_file_directory(dir_path)


def server1_serve():
    # create server for ABAP system ABC
    server = Server({"dest": "gateway"}, {"dest": "MME"}, {"port": 8081, "server_log": False})
    print(server.get_server_attributes())

    # expose python function my_stfc_connection as ABAP function STFC_CONNECTION, to be called by ABAP system
    server.add_function("STFC_CONNECTION", my_stfc_connection)

    # start server
    server.serve()


def server2_serve():
    # create server for ABAP system XYZ
    server = Server({"dest": "gatewayqm7"}, {"dest": "QM7"}, {"port": 8081, "server_log": False})
    print(server.get_server_attributes())

    # expose python function my_stfc_structure as ABAP function STFC_STRUCTURE, to be called by ABAP system
    server.add_function("STFC_STRUCTURE", my_stfc_structure)

    # start server
    server.serve()

# start servers

server1_thread = Thread(target=server1_serve)
server1_thread.start()
print("Server1 started")

server2_thread = Thread(target=server2_serve)
server2_thread.start()
print("Server2 started")

input("Press Enter to stop server1...")

server1_thread.join()

input("Press Enter to stop server2...")
server2_thread.join()

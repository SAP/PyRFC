import os
from pyrfc import Server, set_ini_file_directory

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

# create server for ABAP system ABC
server1 = Server({"dest": "gateway"}, {"dest": "MME"}, {"port": 8081, "server_log": False})

# expose python function my_stfc_connection as ABAP function STFC_CONNECTION, to be called by ABAP system
server1.add_function("STFC_CONNECTION", my_stfc_connection)

# start 1st server
server1.start()

# get server attributes
print("server1", server1.get_server_attributes())

# create server for ABAP system XYZ
server2 = Server({"dest": "gatewayqm7"}, {"dest": "QM7"}, {"port": 8081, "server_log": False})

# expose python function my_stfc_structure as ABAP function STFC_STRUCTURE, to be called by ABAP system
server2.add_function("STFC_STRUCTURE", my_stfc_structure)

# start 2nd server
server2.start()

# get server attributes
print("server2", server2.get_server_attributes())

# stop server
input("Press Enter to stop servers...")

server1.stop()
print("Server 1 stoped")

server2.stop()
print("Server 2 stoped")
